# How to work with it

## Opening project

### VSCode

1. Open VSCode
2. Select File -> Open Folder and find study_to_sola from your Desktop

### Terminal

1. Open Terminal
2. type `cd Desktop/study_to_sola`

## Starting work (branching out and back to main)

### Create your own feature branch

0. You should be in Terminal, once you done step from Opening project chapter
1. Type: `git checkout main` and after that type: `git pull origin main`
2. Type: `git checkout -b feature/YOUR_BRANCH_NAME` (not in caps lock)

-   Do your programming here

3. Once you have made your change type: `git add .`
4. Type: `git commit -m "DESCRIBE THE CHANGE YOU MADE HERE"` (not in capse lock)
5. Type: `git push origin feature/YOUR_BRANCH_NAME` branch name you need to use from the second step
6. Type: `git checkout origin main`
