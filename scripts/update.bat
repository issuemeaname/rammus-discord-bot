echo off
cls

cd ..
heroku ps:scale worker=0
git commit -am "Prepare for deployment"
git push heroku prepare-to-deploy:master
heroku ps:scale worker=1
