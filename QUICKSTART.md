# XMA v0.1.0 quick start

Extract the Linux x86_64 candidate bundle and run:

```bash
./xma --help
./xma version
./xma status --repository /path/to/repository
```

Authenticated operations use Firefox locally without exporting cookies:

```bash
./xma download @HANDLE --limit 1 --repository /path/to/repository \
  --auth-browser firefox --auth-profile PROFILE_NAME
```

This candidate is limited to ten videos and is not certified for bulk unattended operation.
