:: Updates current version of Rammus if any updates have been pushed on my end
set DIR=%userprofile%\Documents\Github

:: if github directory does not exist, create it
if not exist %DIR% mkdir %DIR%
:: if current directory is not github directory, set accordingly
if not %DIR%==%CD% cd %DIR%

git pull https://github.com/issuemeaname/rammus-discord-bot.git
