# Chocolate Joe

Conversational telegram chatbot playing a role of a legendary pirate - Captain Chocolate Joe!

## Last Update

- Add configurable notifications to the chatbot
  - You can now enable or disable release notifications for your chat (enabled by default)
- Add automatic release notes provided by Chocolate Joe automatically! How cool is that?
- Improve the system messages to make them more representative
- Add @mentions (@chocolate_joe_bot) handling
- Replying to Chocolate Joe's messages now grabs his attention too!
- More intuitive private chat flow:
  - Chocolate Joe now responds to any private message (you didn't just corner him for nothing, did you?)

## Roadmap

### Features

- [x] Processing of tags and replies
- [ ] Chatbot memory
- [ ] Chatbot knowledge base
- [ ] Multimodal message processing

### QoL

- [x] Provide constant uptime
- [x] User-friendly release notes provided by Chocolate Joe himself
- [x] Zero-downtime updates
- [ ] Inline command manual(?)

### Tech

- [x] Basic server running a container
- [x] Fully automated deployment (partially done)
- [ ] Better configuration storage
- [ ] Gradually move to langchain

## Tech

- Python
- Telegram Bot API
- GPT-OSS 120B
- Redis
