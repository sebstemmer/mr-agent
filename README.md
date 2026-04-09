# mr-agent

## Run Postgres locally

```bash
docker run -d --name mr-agent-pg -e POSTGRES_USER=mr_agent -e POSTGRES_PASSWORD='<password>' -e POSTGRES_DB=mr_agent -p 5432:5432 -v mr-agent-pg-data:/var/lib/postgresql postgres:18
```

## Update dependencies

```bash
./update_deps.sh
```

## Deployment

### 1. Create SSH key for GitHub Actions

```bash
ssh-keygen -t ed25519 -C "github" -f ansible/github
```

### 2. Add secrets to GitHub

Go to repo -> Settings -> Secrets and variables -> Actions:

- `SSH_KEY` - contents of the `github` private key file
- `SERVER_IP` - your server's IP address

Delete the private key after:

```bash
rm ansible/github
```

### 3. Create production environment file

Set the Postgres connection variables:

```
POSTGRES_USER=mr_agent
POSTGRES_PASSWORD=<password>
POSTGRES_HOST=postgres
POSTGRES_DB=mr_agent
```

### 4. Create Ansible inventory

```bash
cp ansible/inventory.yml.example ansible/inventory.yml
```

Fill in your server IP and SSH key path.

### 5. Run Ansible

```bash
ansible-playbook -i ansible/inventory.yml ansible/setup.yml
```