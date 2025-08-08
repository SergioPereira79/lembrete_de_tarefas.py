#Persistent ; Mantém o script rodando
#SingleInstance, Force ; Garante que apenas uma versão do script rode

; --- Configurações (fácil de mudar aqui) ---
InactivityMinutes := 30
TargetURL := "https://keep.google.com/"
; --- Fim das Configurações ---

InactivityTimeMS := InactivityMinutes * 60 * 1000
WasInactive := false

; Inicia o temporizador que verifica a inatividade a cada 5 segundos
SetTimer, CheckIdle, 5000
Return

CheckIdle:
    ; A_TimeIdle é uma variável interna do AutoHotkey que mede o tempo de inatividade
    if (A_TimeIdle > InactivityTimeMS)
    {
        WasInactive := true
    }
    ; Se o usuário estava inativo e agora mexeu (tempo de inatividade resetou para menos de 5s)
    else if (WasInactive and A_TimeIdle < 5000)
    {
        Run, %TargetURL% ; Abre o link
        WasInactive := false ; Reseta a flag
    }
return

; Para pausar e despausar o script, você pode usar um atalho de teclado.
; Exemplo: Pressione Ctrl + Alt + P para pausar/despausar
^!p::Pause