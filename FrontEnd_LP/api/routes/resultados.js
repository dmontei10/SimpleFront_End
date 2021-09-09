const User = require("../sequelize");
const Detections = User;

module.exports = (app) => {
  app.get("/resultados", (req, res, next) => {
        Detections.findAll()
        .then((detections) => {
            //console.log("Todos os resultados: ", JSON.stringify(detections, null, 2));
            res.status(200).send(JSON.stringify(detections,null, 2));
        });
      });
};