echo off
cls


cd ..
git commit -am "Prepare for deployment"
git push heroku prepare-to-deploy:master
heroku run python rammus.py shell
pause
