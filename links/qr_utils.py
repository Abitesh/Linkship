import qrcode
from io import BytesIO

from django.core.files.base import ContentFile

from .models import Link


def generate_qr_for_link(link: Link, *, overwrite: bool = False) -> None:
    """
    Generate a QR code PNG for this link's full short URL and store it in
    link.qr_code_image.

    - Uses Link.get_full_short_url() as the QR target.
    - Does nothing if qr_code_image already exists unless overwrite=True.
    """
    if link.qr_code_image and not overwrite:
        return

    data = link.get_full_short_url()
    if not data:
        # No usable short URL yet; don't try to generate QR.
        return

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    file_name = f'link_{link.id}_qr.png'
    link.qr_code_image.save(file_name, ContentFile(buffer.getvalue()), save=True)