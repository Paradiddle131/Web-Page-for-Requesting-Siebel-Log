const User = require("../models/user.js")
const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const passport = require('passport');
require('dotenv').config();

//login handle
router.get('/login', (req, res) => {
    res.render('login');
})
router.post('/login', (req, res, next) => {
    passport.authenticate('local', {
        successRedirect: process.env.HOST_ADDRESS,
        failureRedirect: '/users/login',
        failureFlash: true,
    })(req, res, next);
})

//logout
router.get('/logout', (req, res) => {
    req.logout();
    req.flash('success_msg', 'Now logged out');
    res.redirect('/users/login');
})
module.exports = router;