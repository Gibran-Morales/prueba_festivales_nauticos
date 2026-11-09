require('dotenv').config({ path: './config/.env' });
const express = require('express');
const path = require('path');
const fs = require('fs');
const app = express();
const PORT = process.env.PORT || 3000;

// Middlewares para leer formularios HTML (urlencoded) y peticiones fetch (JSON)
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Middleware de autenticación (Simulado)
const verifyCore62Auth = (req, res, next) => {
    const isAuth = true; 
    if(isAuth) next();
    else res.status(401).send('Acceso denegado: Se requiere autenticación CORE-62');
};

// Función auxiliar para guardar registros de formularios en backend/data/leads.json
const leadsFilePath = path.resolve(__dirname, './data/leads.json');
function saveLead(tipoFormulario, datos) {
    let leads = [];
    try {
        if (fs.existsSync(leadsFilePath)) {
            leads = JSON.parse(fs.readFileSync(leadsFilePath, 'utf8'));
        }
    } catch (e) {
        leads = [];
    }
    const nuevoRegistro = {
        id: Date.now(),
        fecha: new Date().toISOString(),
        formulario: tipoFormulario,
        ...datos
    };
    leads.push(nuevoRegistro);
    fs.mkdirSync(path.dirname(leadsFilePath), { recursive: true });
    fs.writeFileSync(leadsFilePath, JSON.stringify(leads, null, 2), 'utf8');
    return nuevoRegistro;
}

// ENDPOINTS DE LOS 3 FORMULARIOS (/api/...)
// 1) Formulario de Solicitud de Patrocinio (frontend/index.html)
app.post('/api/patrocinio', (req, res) => {
    const registro = saveLead('patrocinio_general', req.body);
    console.log('📩 Nueva solicitud de Patrocinio:', registro);
    if (req.headers.accept && req.headers.accept.includes('application/json')) {
        return res.status(200).json({ ok: true, mensaje: 'Solicitud de patrocinio registrada', registro });
    }
    return res.redirect('/#patrocinio');
});

// 2) Formulario de Confirmación República de Panamá (frontend/alianzas/panama.html)
app.post('/api/panama-confirmacion', (req, res) => {
    const registro = saveLead('confirmacion_panama', req.body);
    console.log('🇵🇦 Nueva confirmación de Panamá:', registro);
    if (req.headers.accept && req.headers.accept.includes('application/json')) {
        return res.status(200).json({ ok: true, mensaje: 'Confirmación de Panamá registrada', registro });
    }
    return res.redirect('/alianzas/panama.html');
});

// 3) Formulario de Confirmación CONCANACO-SERVYTUR (frontend y dashboard)
app.post('/api/concanaco-confirmacion', (req, res) => {
    const registro = saveLead('confirmacion_concanaco', req.body);
    console.log('🏛️ Nueva confirmación de CONCANACO:', registro);
    if (req.headers.accept && req.headers.accept.includes('application/json')) {
        return res.status(200).json({ ok: true, mensaje: 'Confirmación de CONCANACO registrada', registro });
    }
    return res.redirect('/alianzas/concanaco.html');
});

// Endpoint privado para consultar desde el Dashboard los registros recibidos
app.get('/api/leads', verifyCore62Auth, (req, res) => {
    try {
        const data = fs.existsSync(leadsFilePath) ? JSON.parse(fs.readFileSync(leadsFilePath, 'utf8')) : [];
        res.json(data);
    } catch (e) {
        res.json([]);
    }
});

// RUTAS ESTÁTICAS (FRONTEND PÚBLICO Y DASHBOARD PRIVADO)
// 1. CAPA PÚBLICA: Sirve /frontend
const frontendPath = path.resolve(__dirname, './frontend');
app.use(express.static(frontendPath));

// 2. CAPA PRIVADA UNIFICADA: Sirve /dashboard (incluye index.html, /estados y /marcas)
const dashboardPath = path.resolve(__dirname, './dashboard');
app.use('/dashboard', verifyCore62Auth, express.static(dashboardPath));

// INICIO DEL SERVIDOR: Escuchando en 0.0.0.0 para permitir acceso en red local
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Servidor CORE-62 activo en el puerto ${PORT}`);
    console.log(`🌐 Acceso local: http://localhost:${PORT}/`);
    console.log(`📡 Acceso en red: http://192.168.1.88:${PORT}/`);
    console.log(`🔒 Dashboard y Propuestas Privadas: http://localhost:${PORT}/dashboard`);
});