{{/* The name of the job and of its ConfigMap. A literal, because the cell chart aliases this chart as vaultConfig and Helm would put that alias, not a valid Kubernetes name, in .Chart.Name. */}}
{{- define "vault-config.name" -}}
vault-config
{{- end -}}

{{/* The labels of every object of the chart. */}}
{{- define "vault-config.labels" -}}
app.kubernetes.io/name: {{ include "vault-config.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "vault-config-%s" .Chart.Version }}
{{- end -}}
