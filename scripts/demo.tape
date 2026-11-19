Output assets/demo.gif

Set Theme {"background":"#080a0c","foreground":"#f2f5f7","selection":"#242b31","cursor":"#ffffff","cursorAccent":"#080a0c","black":"#080a0c","brightBlack":"#6b757d","red":"#ff5f56","brightRed":"#ff5f56","green":"#27c93f","brightGreen":"#27c93f","yellow":"#ffbd2e","brightYellow":"#ffbd2e","blue":"#c6ced3","brightBlue":"#e3e9ec","magenta":"#aab4bb","brightMagenta":"#f2f5f7","cyan":"#d6dde2","brightCyan":"#ffffff","white":"#f2f5f7","brightWhite":"#ffffff"}

Set Shell "bash"
Set FontFamily "Menlo"
Set FontSize 18
Set Width 1200
Set Height 420
Set Padding 20
Set BorderRadius 12
Set WindowBar "Rings"
Set TypingSpeed 30ms
Set Framerate 30
Env PS1 "greyson@mac ~ % "

Type "cargo build -p horizon --release"
Sleep 500ms
Enter
Sleep 1800ms
Type "ipsw extract --dyld"
Sleep 400ms
Enter
Sleep 1500ms
Type "qmlscene SekaiPop"
Sleep 400ms
Enter
Sleep 1600ms
