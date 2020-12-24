const express = require('express');
const router = express.Router();
const app = express();
const mongoose = require('mongoose');
const expressEjsLayout = require('express-ejs-layouts')
const session = require('express-session');
const flash = require('connect-flash');
const passport = require('passport');
app.use(express.static('public'));
require("./config/passport")(passport)
//mongoose
// mongoose.connect('mongodb://localhost:27017/dbname', {useNewUrlParser: true, useUnifiedTopology : true})
mongoose.connect('mongodb+srv://botAdmin:ksgnBbGF2lQGTLXM@whatsappcluster.p1ato.mongodb.net/test?authSource=admin&replicaSet=atlas-vz7qzu-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true', {
        useNewUrlParser: true,
        useUnifiedTopology: true
    })
    .then(() => console.log('connected,,'))
    .catch((err) => console.log(err));
//EJS
app.set('view engine', 'ejs');
app.use(expressEjsLayout);
//BodyParser
app.use(express.urlencoded({
    extended: false
}));
//express session
app.use(session({
    secret: 'secret',
    resave: true,
    saveUninitialized: true
}));
app.use(passport.initialize());
app.use(passport.session());
//use flash
app.use(flash());
app.use((req, res, next) => {
    res.locals.success_msg = req.flash('success_msg');
    res.locals.error_msg = req.flash('error_msg');
    res.locals.error = req.flash('error');
    next();
})
//Routes
app.use('/', require('./routes/index'));
app.use('/users', require('./routes/users'));

app.listen(3000);