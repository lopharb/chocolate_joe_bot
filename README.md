# Chocolate Joe

Conversational telegram chatbot playing a role of a legendary pirate - Captain Chocolate Joe!

## Last Update

- Add memory: Joe now remembers everything that was going on in the chat for the last 5 minutes.
  - It's a not-so-stable feature atm, feel free to submit bug reports
- Significantly improved Joe's soft skills. He's much less aggressive now
  - This is still subject to change, tune etc.

## Roadmap

### Features

- [x] Processing of tags and replies
- [x] Chatbot memory
- [ ] Chatbot knowledge base
- [ ] Multimodal message processing

### QoL

- [x] Provide constant uptime
- [x] User-friendly release notes provided by Chocolate Joe himself
- [x] Zero-downtime updates
- [ ] Inline command manual(?)
- [ ] Message topic validation

### Tech

- [x] Basic server running a container
- [x] Fully automated deployment (partially done)
- [ ] Better configuration storage
- [x] Gradually move to langchain
- [ ] Pydantic message verification
- [ ] Memory safety mechanism

## Stack

- Python
- Telegram Bot API
- GPT-OSS 120B
- Redis
