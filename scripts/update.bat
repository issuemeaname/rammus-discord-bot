echo off
cls

cd ..
git commit -am "Prepare for deployment"
git push heroku prepare-to-deploy:master
heroku ps:scale worker=1
