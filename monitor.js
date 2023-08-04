const https = require('https');
const crypto = require('node:crypto');
const ossl = require('openssl-wrapper');

const pinnedCert = [
  {
    pki: '',
    sha256fingerprint: ''
  },
  {
    pki: '',
    sha256fingerprint: ''
  }
]

function getPublicKey(certificate,level) {
  ossl.exec('x509', certificate, { inform: 'der', outform: 'pem' }, (err, buffer) => {
    const publicKey = buffer.toString('utf8'); // PEM encoded public key safe to use now
    console.log(publicKey,level,sha256(publicKey))
    if (sha256(publicKey) === pinnedCert[level].pki) {
      console.log("Public Key Matches")
    }
    else {
      console.log("Alert: Public Key Does Not match")
    }
  })
}
async function getUrl() {
  const resp = https.get('https://google.edgekey-staging.net', {
    headers: { host: 'www.google.org' }
  }, async res => {
    // console.log('okay', res.headers);
    let cert = res.socket.getPeerCertificate(true);
    let list = new Set();
    let level = 0
    do {
      list.add(cert);
      console.log("Subject:", cert.subject.CN);
      let rawCertificate = cert.raw
      if (level < 2){
        getPublicKey(rawCertificate,level)
      }
      console.log(Buffer.from(cert.fingerprint256).toString('base64'))
      if (Buffer.from(cert.fingerprint256).toString('base64') === pinnedCert[level].sha256fingerprint) {
        console.log("Fingerprint Matches")
      }
      else {
        console.log("Alert: Fingerprint Does Not match")
      }
      level ++;
      cert = cert.issuerCertificate;
    } while (cert && typeof cert === "object" && !list.has(cert));
  }).on('error', e => {
    console.log('E', e.message);
  });
}



getUrl()


function sha256(input) {
  return crypto.createHash('sha256').update(input).digest('hex');
}
