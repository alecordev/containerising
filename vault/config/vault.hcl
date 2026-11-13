# Non-dev Vault: file storage, plain HTTP listener, UI on. Local development only (no TLS!).
# Used by the `vault-persistent` service (compose profile `persistent`).
ui            = true
disable_mlock = true

storage "file" {
  path = "/vault/file"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = true
}

api_addr = "http://127.0.0.1:8200"
