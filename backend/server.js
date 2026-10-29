require('dotenv').config({ path: './config/.env' });
const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware de autenticación (Simulado)
const verifyCore62Auth = (req, res, next) => {
    const isAuth = true; 
    if(isAuth) next();
    else res.status(401).send('Acceso denegado: Se requiere autenticación CORE-62');
};

// 1. CAPA PÚBLICA: Solo sirve lo que está en /frontend
const frontendPath = path.resolve(__dirname, '../frontend');
app.use(express.static(frontendPath));

// 2. CAPA PRIVADA UNIFICADA: Todo lo que no es público vive dentro de /dashboard
// Esto protege el tablero (/dashboard), los 32 estados (/dashboard/estados/...),
// las 19 marcas (/dashboard/marcas/...) y los documentos (/dashboard/documentos/...)
const dashboardPath = path.resolve(__dirname, '../dashboard');
app.use('/dashboard', verifyCore62Auth, express.static(dashboardPath));

app.listen(PORT, () => {
    console.log(`🚀 Servidor CORE-62 activo en http://localhost:${PORT}`);
    console.log(`🌐 Sitio Público: http://localhost:${PORT}/`);
    console.log(`🔒 Dashboard y Propuestas Privadas: http://localhost:${PORT}/dashboard`);
});