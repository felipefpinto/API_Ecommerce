from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from api_ecommerce.core.config import settings


message = Mail(
    from_email=settings.sendgrid_from_email,
    to_emails=settings.sendgrid_from_email,
    subject="Teste SendGrid - iComida",
    html_content="""
        <h2>Teste do iComida</h2>
        <p>Se você recebeu este e-mail, o SendGrid está funcionando.</p>
    """,
)

try:
    sg = SendGridAPIClient(settings.sendgrid_api_key)
    response = sg.send(message)

    print("Status:", response.status_code)

except Exception as erro:
    print("Erro ao enviar e-mail:")
    print(erro)