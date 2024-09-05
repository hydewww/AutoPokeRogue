# AutoPokeRogue

English / [中文文档](./README_CN.md)

Automate [PokeRogue](https://pokerogue.net)'s `Daily Run` based on [Daily Run Guide](https://www.reddit.com/r/pokerogue/?f=flair_name%3A%22Daily%20Run%20Guide%22), by OCR and emulated keyboard input.

![example](example.gif)

```
⚠ Note ⚠
1. The project needs to be runned in the foreground
2. Still WIP. Due to possible errors in command recognition，it cannot be guaranteed to be 100% correctly executed.
```


## Get Started

### Prerequisites

- Chrome
- Python
- pip

### Setup

1. Code
   1. Clone code
   2. Install dependencies ```pip install -r requirements.txt```
   3. Create the configuration file(`config.json`) ```python config.py```
2. Cookie (Don't share your cookies)
   1. Log in to pokerogue in Chrome
   2. View Cookies （[Tutorial](https://developer.chrome.com/docs/devtools/application/cookies#open)）
   3. Fill in the value of the `pokerogue_sessionId` field into `COOKIE` in `config.json`
3. Chrome Driver
   1. Update Chrome
   2. Download [chromedriver](https://googlechromelabs.github.io/chrome-for-testing/) according to your computer platform
   3. Unzip and place the `chromedriver` binary into the code directory

### Daily Run

1. Activate the daily challenge（to make sure you can enter the challenge you want by `Continue`）
   1. New：refresh=>`Daily Run`=>choose slot=>`Menu`=>`Save And Quit`
   2. Existing：Refresh=>`Load Game`=>choose slot=>`Menu`=>`Save And Quit`
2. Get Guide
   1. Find the [Daily Run Guide](https://www.reddit.com/r/pokerogue/?f=flair_name%3A%22Daily%20Run%20Guide%22) corresponding to the Daily Run date
   2. Copy the instructions in `Spreadsheet Guides`.`Pastebin`（`Text-Based Version` is also correct, but when the instructions are modified, generally only the Google Doc will be updated）
   3. Create a `daily.txt` file in the code directory, paste the instructions and save it
3. Run `python machine.py`

## FAQ

### Browser flickers

Caused by screenshot, there is no solution found yet 

## TODO

- [x] Identify shiny
- [ ] Training ocr by fonts
- [ ] ~~Simple automatic battle? (e.g. Endless mode)~~
