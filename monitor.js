const https = require('https');
const crypto = require('crypto');
const assert = require("assert");

const members1stSPKI = ''
const intermediateCertificateSPKI = ''

function sha256(input) {
  return crypto.createHash('sha256').update(input).digest();
}

function getCertificateSPKI(certificate){
  const pemHeader = '-----BEGIN CERTIFICATE-----\n';
  const pemFooter = '-----END CERTIFICATE-----\n';
  const base64Cert = certificate.toString('base64');
  let pemCertificate = pemHeader;
  for (let i = 0; i < base64Cert.length; i += 64) {
    pemCertificate += base64Cert.slice(i, i + 64) + '\n';
  }
  pemCertificate += pemFooter;
  let pkey = crypto.createPublicKey(pemCertificate).export({ type: 'spki', format: 'der' })
  return Buffer.from(sha256(Buffer.from(pkey))).toString('base64');
}


const resp = https.get('https://members1st.edgekey-staging.net', {
  headers: { host: 'www.members1st.org' }
}, async res => {

  const certificate = res.socket.getPeerCertificate(true);
  const members1stCertificate = certificate.raw
  const intermediateCertificate = certificate.issuerCertificate.raw

  assert.equal(res.headers['x-akamai-staging'],'ESSL','Failed to hit the Staging Endpoint')
  assert.equal(getCertificateSPKI(members1stCertificate),members1stSPKI,'members1st.org SPKI Hash Does Not Match')
  assert.equal(getCertificateSPKI(intermediateCertificate),intermediateCertificateSPKI,'Intermediate Certificate SPKI Hash Does Not Match')
}).on('error', e => {
  console.log('Error', e.message);
});
