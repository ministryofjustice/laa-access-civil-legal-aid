#####################################################################
## The following is only required for the demos and can be removed ##
#####################################################################

# Remove existing GOV.UK Frontend test fixtures
rm -rf govuk_components

# Get new release source code and move to a directory
curl -L https://github.com/alphagov/govuk-frontend/archive/refs/tags/v5.3.0.zip > govuk_frontend_source.zip
unzip -o govuk_frontend_source.zip -d govuk_frontend_source
mkdir govuk_components
mv govuk_frontend_source/govuk-frontend-5.3.0/packages/govuk-frontend/src/govuk/components/** govuk_components

# Remove all files apart from test fixtures
find govuk_components -type f ! -name '*.yaml' -delete

# Tidy up
rm -rf govuk_frontend_source
rm -rf govuk_frontend_source.zip
