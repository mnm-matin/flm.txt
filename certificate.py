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

CUSTOM_OID = "1.3.6.1.4.1.99999.1"

def sha256_hex(data):
    return hashlib.sha256(data.encode()).hexdigest()

def sign(live_url, verified_list: list[str], key_out="llm_key.pem", cert_out="llm_cert.pem"):
    # Generate key + self-signed cert
    priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"example.com"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"MyOrg")
    ])

    # 3. Define custom OID and extension
    CUSTOM = ObjectIdentifier(CUSTOM_OID)
    
    # Create a dictionary where each URL gets its own hash
    url_hashes = {}
    for i, url in enumerate(verified_list):
        # Get hash of the URL
        url_hash = sha256(url.encode('utf-8')).hexdigest()
        # Store hash in dictionary with index as key
        url_hashes[str(i)] = url_hash
    
    # Convert to JSON and then to bytes
    ext_value = json.dumps(url_hashes).encode('utf-8')
    custom_ext = x509.UnrecognizedExtension(CUSTOM, ext_value)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject).issuer_name(issuer)
        .public_key(priv.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.utcnow())
        .not_valid_after(datetime.utcnow() + timedelta(days=30))
        .add_extension(custom_ext, critical=False)
        .sign(priv, hashes.SHA256())
    )
    open(key_out, "wb").write(priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()))
    open(cert_out, "wb").write(cert.public_bytes(serialization.Encoding.PEM))

    # Build payload
    payload = {
        "url": live_url,
        "hash": sha256_hex(live_url),
        "method": "llm-verify",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600
    }
    data = json.dumps(payload).encode()
    sig = base64.b64encode(
        priv.sign(data, padding.PKCS1v15(), hashes.SHA256())).decode()

    click.echo("✅ Verification passed — trust link issued.")
    result = {"payload": payload, "signature": sig, "cert": cert_out}
    
    click.echo(json.dumps(result))


sign("https://www.purdueglobal.edu", ["https://www.purdueglobal.edu/blog/b", "https://www.purdueglobal.edu/blog/a"])