targetScope = 'resourceGroup'

param location string = resourceGroup().location
param serviceName string = 'orbit-campaign-pilot001'
param containerImage string
param containerAppsEnvironmentId string
param userAssignedIdentityId string
param cosmosEndpoint string
param azureSubscriptionId string
param acrServer string = 'crorbitplatform.azurecr.io'

resource appi 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-${serviceName}'
  location: location
  kind: 'web'
  properties: { Application_Type: 'web' }
}

resource ca 'Microsoft.App/containerApps@2024-03-01' = {
  name: serviceName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerAppsEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8000
        transport: 'auto'
      }
      registries: [
        {
          server: acrServer
          identity: userAssignedIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'app'
          image: containerImage
          env: [
            { name: 'CAMPAIGN_ID', value: 'd00ca9db-6544-46ae-a8d4-c6de76d5bfba' }
            { name: 'CAMPAIGN_SLUG', value: 'pilot001' }
            { name: 'AZURE_SUBSCRIPTION_ID', value: azureSubscriptionId }
            { name: 'AZURE_RESOURCE_GROUP', value: resourceGroup().name }
            { name: 'STORAGE_ACCOUNT_NAME', value: 'stcamppilot001' }
            { name: 'KEY_VAULT_NAME', value: 'kv-orbit-camp-pilot001' }
            { name: 'COSMOS_ENDPOINT', value: cosmosEndpoint }
            { name: 'PUBLIC_BASE_URL', value: 'https://pilot001.campaigns.wakaorbit.com' }
            { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appi.properties.ConnectionString }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output containerAppName string = ca.name
output fqdn string = ca.properties.configuration.ingress.fqdn
