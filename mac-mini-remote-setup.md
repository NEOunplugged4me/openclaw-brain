# Mac Mini Remote Access Setup

**Host:** Mac-193.lan (kims-mac-mini on Tailscale)
**User:** kimbot
**Local IP:** 192.168.1.105
**Tailscale IP:** 100.75.144.127
**Status:** ✅ SSH on, Screen Sharing on, Tailscale on

## Step 1: Run these on the Mac mini (in Terminal, needs password)

```bash
# Enable SSH
sudo systemsetup -setremotelogin on

# Enable Screen Sharing
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist

# Install Tailscale
brew install --cask tailscale
```

Then open the **Tailscale** app and sign in.

## Step 2: Run these on the MacBook

```bash
# Install Tailscale
brew install --cask tailscale
```

Open Tailscale and sign in with the **same account**.

## Step 3: Connect from the MacBook

```bash
# Get the Mac mini's Tailscale IP
tailscale status

# SSH
ssh kimbot@100.75.144.127

# Screen Sharing (Finder > Go > Connect to Server)
vnc://kimbot@100.75.144.127
```

## Local network (same WiFi only)

```bash
ssh kimbot@192.168.1.105
# Screen Sharing: vnc://kimbot@192.168.1.105
```

## SSH config shortcut (add to MacBook's ~/.ssh/config)

```
Host mini
    HostName 100.75.144.127
    User kimbot
```

Then just: `ssh mini`
