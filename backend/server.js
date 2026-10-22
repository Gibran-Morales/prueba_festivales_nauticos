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

// Asegurar ruta al frontend
const frontendPath = path.resolve(__dirname, '../frontend');
app.use(express.static(frontendPath));

// Forzar la ruta raíz a servir el index.html
app.get('/', (req, res) => {
    res.sendFile(path.join(frontendPath, 'index.html'));
});

// Dashboard Privado
app.use('/dashboard', verifyCore62Auth, express.static(path.join(__dirname, '../dashboard/views')));

app.listen(PORT, () => {
    console.log(`Servidor CORE-62 corriendo en http://localhost:${PORT}`);
});
