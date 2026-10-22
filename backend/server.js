require('dotenv').config({ path: './config/.env' });
const express = require('express');
const path = require('path');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware para verificar autenticación de usuarios CORE-62
const verifyCore62Auth = (req, res, next) => {
    // Simulación de sesión activa para pruebas locales
    const isAuth = true; 
    if(isAuth) next();
    else res.status(401).send('Acceso denegado: Se requiere autenticación CORE-62');
};

// 1. FRONTEND (Información Pública)
app.use(express.static(path.join(__dirname, '../frontend')));

// 2. DASHBOARD Y REPORTES (Información Privada)
// IMPORTANTE: Esta ruta es a la que apunta el botón "Acceso Dashboard" del index.html
app.use('/dashboard', verifyCore62Auth, express.static(path.join(__dirname, '../dashboard/views')));

app.listen(PORT, () => {
    console.log(`Servidor CORE-62 corriendo en http://localhost:${PORT}`);
});
