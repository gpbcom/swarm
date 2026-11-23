{{/*
Check the values the simulator cannot run without, and fail naming the one that is missing.
*/}}
{{- define "simulator.validate" -}}
{{- $_ := required "operatorId is required: set the identifier of the Operator." .Values.operatorId -}}
{{- $_ := required "image.tag is required: set the tag of the simulator image." .Values.image.tag -}}
{{- $_ := required "px4Sitl.image.tag is required: set the tag of the PX4 SITL image." .Values.px4Sitl.image.tag -}}
{{- end -}}
