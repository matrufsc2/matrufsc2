echo "Deleting old content"
rm -Rf public coverage_*.json coverage report.tap
echo "Running Coverage Server"
node coverage_server.js &
echo "Getting PID of the coverage server"
COVERAGE_SERVER=$?
echo "Running Test'em CI"
testem ci | tee report.tap
echo "Killing Coverage Server"
kill $COVERAGE_SERVER


