{{/* Chart name */}}
{{- define "stockpilot.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Fully qualified app name: <release>-stockpilot (or just the release when it already contains the chart name) */}}
{{- define "stockpilot.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "stockpilot.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* Common labels applied to every object */}}
{{- define "stockpilot.labels" -}}
helm.sh/chart: {{ include "stockpilot.chart" . }}
app.kubernetes.io/name: {{ include "stockpilot.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: stockpilot
{{- end }}

{{/* Selector labels for a component: include "stockpilot.selectorLabels" (dict "root" . "component" "backend") */}}
{{- define "stockpilot.selectorLabels" -}}
app.kubernetes.io/name: {{ include "stockpilot.name" .root }}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end }}

{{- define "stockpilot.backend.fullname" -}}{{ include "stockpilot.fullname" . }}-backend{{- end }}
{{- define "stockpilot.frontend.fullname" -}}{{ include "stockpilot.fullname" . }}-frontend{{- end }}
{{- define "stockpilot.postgres.fullname" -}}{{ include "stockpilot.fullname" . }}-postgres{{- end }}

{{/* Name of the secret holding PostgreSQL credentials */}}
{{- define "stockpilot.postgres.secretName" -}}
{{- if .Values.postgres.existingSecret }}{{ .Values.postgres.existingSecret }}{{ else }}{{ include "stockpilot.postgres.fullname" . }}{{ end }}
{{- end }}

{{/* Hostname the backend should use to reach PostgreSQL */}}
{{- define "stockpilot.postgres.host" -}}
{{- if .Values.postgres.enabled }}{{ include "stockpilot.postgres.fullname" . }}{{ else }}{{ required "postgres.host is required when postgres.enabled=false" .Values.postgres.host }}{{ end }}
{{- end }}
