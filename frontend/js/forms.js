// Manejo unificado de formularios FNMX 2026 (API Backend + WhatsApp + Mensaje de Confirmación)
document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form[action^="/api/"]');

    forms.forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn ? submitBtn.innerHTML : 'Enviar';
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '⏳ Procesando solicitud...';
            }

            const formData = new FormData(form);
            const payload = Object.fromEntries(formData.entries());
            // Si hay múltiples checkboxes con el mismo nombre (ej. embarcaciones)
            const multiBoats = formData.getAll('embarcacion');
            if (multiBoats.length > 1) {
                payload.embarcacion = multiBoats.join(', ');
            }

            const endpoint = form.getAttribute('action');
            let apiSuccess = false;

            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                if (response.ok) {
                    apiSuccess = true;
                }
            } catch (err) {
                console.warn('Servidor local sin conexión, abriendo respaldo por WhatsApp:', err);
            }

            // Construir mensaje de WhatsApp según el formulario
            let waText = '';
            if (endpoint.includes('patrocinio')) {
                waText = `Hola, soy *${payload.nombre || ''}* (${payload.cargo || 'Directivo'}) de *${payload.empresa || ''}* [Giro: ${payload.giro || ''}]. Solicito información de patrocinio en Festivales Náuticos MX 2026.%0A%0A` +
                         `⛵ Embarcación de interés: ${payload.embarcacion || 'Por definir'}%0A` +
                         `💼 Inversión estimada: ${payload.inversion || 'Por definir'}%0A` +
                         `📧 Correo: ${payload.email || ''}%0A` +
                         `📱 Tel: ${payload.telefono || ''}` +
                         (payload.mensaje ? `%0A📝 Mensaje: ${payload.mensaje}` : '');
            } else if (endpoint.includes('panama-confirmacion')) {
                waText = `Hola, soy *${payload.nombre || ''}* (${payload.cargo || ''}) de *${payload.institucion || ''}*. Confirmo interés de participación para la delegación de la República de Panamá (Ref: FNMX-2026-PA-001).%0A%0A` +
                         `🇵🇦 Modalidad: ${payload.tipo || 'Por definir'}%0A` +
                         `📧 Correo: ${payload.email || ''}` +
                         (payload.mensaje ? `%0A📝 Comentarios: ${payload.mensaje}` : '');
            } else if (endpoint.includes('concanaco-confirmacion')) {
                waText = `Hola, soy *${payload.nombre || ''}* (${payload.cargo || ''}) de *${payload.camara || ''}*. Confirmo interés en la Alianza Estratégica CONCANACO-SERVYTUR × FNMX 2026 (Ref: FNMX-2026-CONC-001).%0A%0A` +
                         `🏛️ Área de interés: ${payload.area || 'Todas las áreas'}%0A` +
                         `📧 Correo: ${payload.email || ''}` +
                         (payload.comentarios ? `%0A📝 Comentarios: ${payload.comentarios}` : '');
            }

            const waUrl = `https://wa.me/5215561184470?text=${waText}`;

            // Mostrar tarjeta de confirmación en lugar del formulario
            const confirmationCard = document.createElement('div');
            confirmationCard.className = 'highlight-box';
            confirmationCard.style.borderLeftColor = '#1f9d55';
            confirmationCard.style.background = 'rgba(31, 157, 85, 0.12)';
            confirmationCard.innerHTML = `
                <h4 style="color:#1f9d55; font-size:1.2rem; margin-bottom:0.5rem;">✅ ¡Solicitud registrada con éxito!</h4>
                <p style="margin-bottom:0.8rem;">Gracias, <strong>${payload.nombre || ''}</strong>. ${apiSuccess ? 'Tus datos han sido guardados en el servidor de CORE-62.' : 'Hemos preparado tu solicitud.'} Nuestro equipo de Dirección General y CORE-62 dará seguimiento inmediato.</p>
                <div style="display:flex; gap:0.8rem; flex-wrap:wrap; margin-top:1rem;">
                    <a href="${waUrl}" target="_blank" class="btn-gold" style="text-decoration:none;">📲 Enviar confirmación por WhatsApp Directo</a>
                    <button type="button" class="btn-outline" id="resetFormBtn">Enviar otra respuesta</button>
                </div>
            `;

            form.style.display = 'none';
            form.parentNode.insertBefore(confirmationCard, form.nextSibling);

            // Abrir WhatsApp automáticamente en nueva pestaña tras breve pausa
            setTimeout(() => {
                window.open(waUrl, '_blank');
            }, 500);

            confirmationCard.querySelector('#resetFormBtn').addEventListener('click', () => {
                form.reset();
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
                confirmationCard.remove();
                form.style.display = 'block';
            });
        });
    });
});