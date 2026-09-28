import re
import random
from datetime import datetime, timedelta, timezone
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from api_ecommerce.core.config import settings

codigos_email: dict[str, dict] = {}

def gerar_codigo_email() -> str:
    return f"{random.randint(0, 999999):06d}"

def enviar_codigo_email(email: str) -> dict:
    email = email.strip().lower()

    if settings.otp_modo.lower() == "dev":
        codigo = "123456"
    else:
        codigo = gerar_codigo_email()

    expira_em = datetime.now(timezone.utc) + timedelta(minutes=10)

    codigos_email[email] = {
        "codigo": codigo,
        "expira_em": expira_em,
    }

    if settings.otp_modo.lower() == "dev":
        return {
            "sucesso": True,
            "mensagem": "Código de desenvolvimento gerado.",
        }

    try:
        message = Mail(
            from_email=settings.sendgrid_from_email,
            to_emails=email,
            subject="Seu código de verificação - iComida",
            html_content=f"""
                <h2>Confirme seu e-mail</h2>

                <p>Use o código abaixo para continuar seu cadastro no iComida:</p>

                <h1>{codigo}</h1>

                <p>Este código é válido por 10 minutos.</p>

                <p>Se você não solicitou este código, ignore este e-mail.</p>
            """,
        )

        sg = SendGridAPIClient(settings.sendgrid_api_key)
        response = sg.send(message)

        if response.status_code not in (200, 201, 202):
            codigos_email.pop(email, None)

            return {
                "sucesso": False,
                "mensagem": "Não foi possível enviar o código por e-mail.",
            }

        return {
            "sucesso": True,
            "mensagem": "Código enviado por e-mail.",
        }

    except Exception as erro:
        print(f"Erro SendGrid: {erro}")

        codigos_email.pop(email, None)

        return {
            "sucesso": False,
            "mensagem": "Não foi possível enviar o código por e-mail.",
        } 

def verificar_codigo_email(
    email: str,
    codigo: str,
) -> dict:
    email = email.strip().lower()

    dados_codigo = codigos_email.get(email)

    if not dados_codigo:
        return {
            "sucesso": False,
            "mensagem": "Nenhum código foi solicitado para este e-mail.",
        }

    if datetime.now(timezone.utc) > dados_codigo["expira_em"]:
        codigos_email.pop(email, None)

        return {
            "sucesso": False,
            "mensagem": "Código expirado. Solicite um novo código.",
        }

    if codigo != dados_codigo["codigo"]:
        return {
            "sucesso": False,
            "mensagem": "Código inválido.",
        }

    # Código usado com sucesso: removemos para impedir reutilização
    codigos_email.pop(email, None)

    return {
        "sucesso": True,
        "mensagem": "Código verificado com sucesso.",
    }

def formatar_celular_twilio(celular: str) -> str:
    numeros = re.sub(r"\D", "", celular)

    # Nosso sistema armazena: DDD + número
    # Exemplo: 11999999999
    if len(numeros) in (10, 11):
        return f"+55{numeros}"

    # Caso já tenha sido enviado com 55
    if len(numeros) in (12, 13) and numeros.startswith("55"):
        return f"+{numeros}"

    raise ValueError("Número de celular inválido.")


def obter_twilio_client() -> Client:
    if not settings.twilio_account_sid or not settings.twilio_auth_token:
        raise RuntimeError("Credenciais da Twilio não configuradas.")

    return Client(
        settings.twilio_account_sid,
        settings.twilio_auth_token,
    )


def enviar_codigo_telefone(celular: str) -> dict:
    if settings.otp_modo.lower() == "dev":
        return {
            "sucesso": True,
            "mensagem": "Código de desenvolvimento gerado.",
        }

    if settings.otp_modo.lower() != "twilio":
        raise RuntimeError("OTP_MODO inválido.")

    if not settings.twilio_verify_service_sid:
        raise RuntimeError("Twilio Verify Service SID não configurado.")

    telefone = formatar_celular_twilio(celular)

    try:
        client = obter_twilio_client()

        client.verify.v2.services(
            settings.twilio_verify_service_sid
        ).verifications.create(
            to=telefone,
            channel="sms",
        )

        return {
            "sucesso": True,
            "mensagem": "Código enviado por SMS.",
        }

    except TwilioRestException as erro:
        print(f"Erro Twilio: {erro}")
        return {
            "sucesso": False,
            "mensagem": "Não foi possível enviar o código por SMS.",
        }


def verificar_codigo_telefone(
    celular: str,
    codigo: str,
) -> dict:
    if settings.otp_modo.lower() == "dev":
        if codigo == "123456":
            return {
                "sucesso": True,
                "mensagem": "Código verificado com sucesso.",
            }

        return {
            "sucesso": False,
            "mensagem": "Código inválido.",
        }

    if settings.otp_modo.lower() != "twilio":
        raise RuntimeError("OTP_MODO inválido.")

    if not settings.twilio_verify_service_sid:
        raise RuntimeError("Twilio Verify Service SID não configurado.")

    telefone = formatar_celular_twilio(celular)

    try:
        client = obter_twilio_client()

        resultado = client.verify.v2.services(
            settings.twilio_verify_service_sid
        ).verification_checks.create(
            to=telefone,
            code=codigo,
        )

        if resultado.status == "approved":
            return {
                "sucesso": True,
                "mensagem": "Código verificado com sucesso.",
            }

        return {
            "sucesso": False,
            "mensagem": "Código inválido ou expirado.",
        }

    except TwilioRestException as erro:
        print(f"Erro Twilio: {erro}")
        return {
            "sucesso": False,
            "mensagem": "Não foi possível verificar o código.",
        }