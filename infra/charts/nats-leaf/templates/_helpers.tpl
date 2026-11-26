{{- define "nats-leaf.remoteUrl" -}}
{{- $url := .Values.remote.url | default "" -}}
{{- if not (hasPrefix "tls://" $url) -}}
{{- fail "remote.url is required and must start with tls://" -}}
{{- end -}}
{{- $url -}}
{{- end -}}

{{- define "nats-leaf.domain" -}}
{{- $domain := .Values.jetstream.domain | default "" -}}
{{- if or (eq $domain "") (eq $domain "cell") -}}
{{- fail "jetstream.domain is required, unique per edge, and must not be cell" -}}
{{- end -}}
{{- $domain -}}
{{- end -}}
