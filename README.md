> NOTE: This repository has been archived and is slated to be removed in the second half of 2024.
> IBM has taken over development of the integration and more recent code may be found at
> https://github.com/omkar-g/integrations-ibm-cloudpak-for-security

# Tenable.io -> IBM Cloud Pak for Security Transformer

This tool is designed to consume Tenable.io asset and vulnerability data,
transform that data into the IBM Cloud Pak for Security format, and then upload
the resulting data into IBM Cloud Pak for Security.

### Requirements

* API Access and Password keys for your IBM Cloud Pak for Security account.
* API Access and Secret keys for an admin user in Tenable.io
* A host to run this integration on.

### Installing Python Requirements
```shell
pip install tenable-ibm-cp4s
```

### Configuration
The following below details both the command-line arguments as well as the
equivalent environment variables.

```
Usage: tenable-ibm-cp4s [OPTIONS]

  Tenable.io -> IBM Security Connect Transformer & Ingester

Options:
  --tio-access-key TEXT         Tenable.io Access Key
  --tio-secret-key TEXT         Tenable.io Secret Key
  -b, --batch-size INTEGER      Export/Import Batch Sizing
  -v, --verbose                 Logging Verbosity
  -s, --observed-since INTEGER  The unix timestamp of the age threshold
  -r, --run-every INTEGER       How many hours between recurring imports
  -a, --ibm-access-key TEXT     The access key for IBMs CAR API.
  -p, --ibm-password-key TEXT   The password key for IBMs CAR API.
  --ibm-car-uri                 The API URI for IBM\'s CAR API.
  --help                        Show this message and exit.
```

### Usage

Run the import once:

```
tenable-ibm-cp4s                        \
    --tio-access-key {TIO_ACCESS_KEY}   \
    --tio-secret-key {TIO_SECRET_KEY}   \
    --ibm-access-key {IBM_ACCESS_KEY}   \
    --ibm-password-key {IBM_PASSWORD_KEY}
```

Run the import once an hour:

```
tenable-ibm-cp4s                          \
    --tio-access-key {TIO_ACCESS_KEY}     \
    --tio-secret-key {TIO_SECRET_KEY}     \
    --ibm-access-key {IBM_ACCESS_KEY}     \
    --ibm-password-key {IBM_PASSWORD_KEY} \
    --run-every 1
```

### Changelog
[Visit the CHANGELOG](CHANGELOG.md)
