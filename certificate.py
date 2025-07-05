import sys, json, time, base64, requests, click, hashlib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography import x509
from cryptography.x509.oid import NameOID, ObjectIdentifier
from datetime import datetime, timedelta
from hashlib import sha256
import json
import os 
from datetime import timezone

CUSTOM_OID = "1.3.6.1.4.1.99999.1"
CERTIFICATE_PATH = 'flm.txt/llm_cert.pem'

def sha256_hex(data):
    return hashlib.sha256(data.encode()).hexdigest()

def sign(live_url, verified_list: list[str]):
    """
    Generate and return a certificate with URL hashes
    
    Args:
        live_url: The URL to verify
        verified_list: List of URLs to verify
        
    Returns:
        tuple: (certificate_pem, private_key_pem)
    """
    # Generate key
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Create certificate subject
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"example.com"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MyOrg")
    ])

    # Create URL hashes
    url_hashes = {}
    for i, url in enumerate(verified_list):
        url_hash = sha256(url.encode('utf-8')).hexdigest()
        url_hashes[str(i)] = url_hash
    
    # Create custom extension
    CUSTOM = ObjectIdentifier(CUSTOM_OID)
    ext_value = json.dumps(url_hashes).encode('utf-8')
    custom_ext = x509.UnrecognizedExtension(CUSTOM, ext_value)

    # Build certificate
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(priv.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=30))
        .add_extension(custom_ext, critical=False)
        .sign(priv, hashes.SHA256())
    )

    # Generate JWT payload
    payload = {
        "url": live_url,
        "hash": sha256_hex(live_url),
        "method": "llm-verify",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }

    # Generate signature
    data = json.dumps(payload).encode()
    sig = priv.sign(data, padding.PKCS1v15(), hashes.SHA256()).decode()

    click.echo("✅ Verification passed — trust link issued.")
    result = {"payload": payload, "signature": sig}
    
    # Return certificate and private key as PEM strings
    cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
    key_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    
    return cert_pem, key_pem


def verify_cert(cert_path=CERTIFICATE_PATH):
    """
    Verify if the certificate contains the LLM verification extension
    
    Args:
        cert_path: Path to the certificate file (relative to project root)
    """
    try:
        # Get the absolute path to the certificate
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cert_path = os.path.join(project_root, cert_path)
        
        # Read certificate from file
        click.echo(f"Reading certificate from {cert_path}...")
        with open(cert_path, 'rb') as f:
            cert_data = f.read()

        cert = x509.load_pem_x509_certificate(cert_data)
        
        # Check for LLM verification extension
        try:
            ext = cert.extensions.get_extension_for_oid(ObjectIdentifier(CUSTOM_OID))
            if isinstance(ext.value, x509.UnrecognizedExtension):
                click.echo(f"✅ Certificate contains LLM verification extension with value: {ext.value.value.decode()}")
            else:
                click.echo("❌ Certificate has LLM verification extension but value format is invalid", err=True)
                sys.exit(1)
        except x509.ExtensionNotFound:
            click.echo("❌ Certificate does not contain LLM verification extension", err=True)
            sys.exit(1)
            
    except Exception as e:
        click.echo(f"❌ Error verifying certificate: {str(e)}", err=True)
        sys.exit(1)

    click.echo("✅ Certificate verification completed")

if __name__ == "__main__":
    cert_pem, key_pem = sign("https://www.purdueglobal.edu", ["https://www.purdueglobal.edu/blog/b", "https://www.purdueglobal.edu/blog/a"])
    verify_cert()  # Uses the default CERTIFICATE_PATH
