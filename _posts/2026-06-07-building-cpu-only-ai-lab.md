---
title: "Building a CPU-only AI Lab from Scratch"
date: 2026-06-07 22:00:00 +0900
categories: [Local LLM, Setup]
tags: [linux, ollama, cpu-inference, home-server]
---

## Why CPU-only?

Most tutorials assume you have an NVIDIA GPU.
I don't. And more importantly — **most real-world edge devices don't either.**

Set-top boxes, industrial controllers, robots, home appliances — they run on CPUs.
If I can make AI work there, I can deploy it *anywhere*.

This is Day 1 of a 6-month project to become an On-device AI Engineer.

---

## The Hardware

Nothing fancy:

```bash
$ lscpu | grep -E "Model name|CPU\(s\)|Thread"
$ free -h
$ df -h
```

> Fill in your actual specs here after running these commands.

The goal: push this machine as far as it can go.

---

## Day 1 Setup

### 1. System Update

```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Install Monitoring Tools

```bash
sudo apt install htop -y
htop
```

First thing any AI engineer should do: **know your resources.**
- How many CPU cores do you have?
- How much RAM is actually free?
- How much disk space for models?

### 3. Directory Structure

```bash
mkdir -p ~/ai-lab/models
mkdir -p ~/ai-lab/projects
mkdir -p ~/ai-lab/logs
```

Clean structure from day one. Models get large fast.

---

## What's Next

**Day 2:** Docker installation — because almost every AI tool ships as a container.

The stack I'm building toward:

```
llama.cpp / Ollama
    ↓
FastAPI (inference server)
    ↓
Docker (containerized deployment)
    ↓
nginx (reverse proxy)
    ↓
Prometheus + Grafana (monitoring)
```

No GPU. No cloud. Just a CPU and engineering.

---

*This post is part of my [6-month On-device AI Engineering roadmap](/about).*
