I see the issue 👇

The critical part of your log is:

```
Error response from daemon: error while mounting volume '/var/lib/docker/volumes/database_18sep_11am_chatbot_storage/_data': 
failed to mount local volume: 
mount /home/abc/chatbot-storage:/var/lib/docker/volumes/database_18sep_11am_chatbot_storage/_data, flags: 0x1000: no such file or directory
```

### What’s happening?

* Docker is trying to mount a **host path volume**:
  `/home/abc/chatbot-storage` → `/var/lib/docker/volumes/.../_data`
* But the path `/home/abc/chatbot-storage` **does not exist** on your host system.
* That’s why Docker fails with `no such file or directory`.

### Why?

This usually happens if:

1. You copied the `docker-compose.yml` from another machine (where `/home/abc/chatbot-storage` existed).
2. You renamed/moved your user home directory (`tuannq` ≠ `abc`).
3. The volume path is hardcoded to `/home/abc/...`, but your actual system uses `/home/tuannq/...`.

### ✅ How to fix

You have two options:

#### 1. Create the missing folder

```bash
sudo mkdir -p /home/abc/chatbot-storage
sudo chown -R 1000:1000 /home/abc/chatbot-storage
```

👉 This makes the path exist so Docker can mount it.
(but maybe `/home/abc` is wrong for your system)

#### 2. Update your `docker-compose.yml`

Find the service that uses this volume (likely `chatbot_storage` or something related).
You’ll see something like:

```yaml
volumes:
  - /home/abc/chatbot-storage:/app/storage
```

Change it to your real path:

```yaml
volumes:
  - /home/tuannq/chatbot-storage:/app/storage
```

or to a relative path (inside your project folder):

```yaml
volumes:
  - ./chatbot-storage:/app/storage
```

---

👉 Tóm lại: lỗi của bạn là **đường dẫn mount volume không tồn tại trên máy thật**.
Bạn muốn tôi chỉ luôn vị trí trong `docker-compose.yml` để sửa cho hợp lý (sử dụng `./chatbot-storage` thay vì hardcode `/home/abc/...`) không?
