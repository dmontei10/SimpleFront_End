module.exports = (sequelize, type) =>
   sequelize.define("detections", {
    id: {
        type: type.INTEGER,
        primaryKey: true,
        autoIncrement: true,
    },  
    frame:{
        type: type.BLOB('longblob'),
        allowNull: false,
        get() {
            return this.getDataValue('frame').toString('base64'); // or whatever encoding is right
          },
    },
    latitude:{
         type: type.DOUBLE,
         allowNull: false,
    },
    longitude:{
        type: type.DOUBLE,
        allowNull: false,
    },
    dataDaDetecao:{
        type: type.DATE,
        allowNull: false,
    },
    percentagemDaDetecao:{
        type: type.DOUBLE,
        allowNull: false,
    },
    fps:{
        type: type.DOUBLE,
        allowNull: false,
    },
    });