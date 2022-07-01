# params=$(cat ${{ inputs.parameterFilePath }})
params=$(cat .parameters/hub.non-prod.parameters.json )
orgId=$(echo $params | jq .parameters.organizationId.value -r)
env=$(echo $params | jq .parameters.environment.value -r)
resourceNumber=$(echo $params | jq .parameters.resourceNumber.value -r)
rgName=$(printf rg-$orgId-$env-%03d $resourceNumber)
echo $rgName