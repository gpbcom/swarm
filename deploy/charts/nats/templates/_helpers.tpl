{{/*
Check the values the cell cannot run without, and fail naming the one that is wrong.
*/}}
{{- define "nats.validate" -}}
{{- $_ := required "auth.operatorJwt is required: set the operator JWT." .Values.auth.operatorJwt -}}
{{- $_ := required "auth.systemAccount is required: set the public key of the system account." .Values.auth.systemAccount -}}
{{- $_ := required "auth.systemAccountJwt is required: set the JWT of the system account." .Values.auth.systemAccountJwt -}}
{{- if lt (int .Values.replicas) 3 -}}
{{- fail (printf "replicas is %v but must be at least 3: JetStream replicas 3 need three servers." .Values.replicas) -}}
{{- end -}}
{{- end -}}
