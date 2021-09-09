const Sequelize = require('sequelize');
const UserModel = require('./models/detections');

const sequelize = new Sequelize('projeto','root','Lab_Proj_7', {
    host:'localhost',
    dialect:'mysql'
});

const User = UserModel(sequelize, Sequelize);

sequelize.sync().then(() => {
    
    console.log('Conectado à base de dados com sucesso!')
}).catch((error) => {
    console.log("Erro ao conectar com a base de dados!", error)
  })
 
  module.exports = User;