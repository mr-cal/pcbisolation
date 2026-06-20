# pcbisolation

Source code for https://pcbisolation.com.

## Deployment

Pushing to `main` triggers `.github/workflows/build.yml`, which:
1. Validates content and checks links with htmlproofer
2. Builds the Hugo site
3. Publishes the result to the `gh-pages` branch
4. Dispatches a `repository_dispatch` event to [mr-cal/vps-infra](https://github.com/mr-cal/vps-infra)

The vps-infra deploy workflow SSHs to the VPS, pulls the latest `gh-pages` commit
via git submodule, and Caddy serves the built site.

Add a `VPSINFRA_PAT` secret to this repo (Settings → Secrets and variables → Actions)
with a fine-grained PAT scoped to `mr-cal/vps-infra` with **Contents: Read and write**.

## Contributing
Feel free to submit an issue or PR!
