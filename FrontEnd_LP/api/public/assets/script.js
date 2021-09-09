//modal do streaming
var modal = document.getElementById("id02");
 
 window.onclick = function(event) {
     if (event.target == modal) {
         modal.style.display = "none";
     }
     
 }     

/* 
  Obter os dados da database
*/
const b64toBlob = (b64Data, contentType='', sliceSize=512) => {
  const byteCharacters = atob(b64Data);
  const byteArrays = [];

  for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    const slice = byteCharacters.slice(offset, offset + sliceSize);

    const byteNumbers = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    const byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  const blob = new Blob(byteArrays, {type: contentType});
  return blob;
}

const urlBase = "http://localhost:8080";
(async () => {
  localStorage.clear();
  const resultados = document.getElementById("id01");
  let txtResultados2 = "";
  let txtResultados = "";
  const response = await fetch(`${urlBase}/resultados`);
  const detections = await response.json(); 
  
  

  txtResultados2 += `

        <div class="container-fluid" id="header">
          <div class="card mt-5">
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-bordered" cellspacing="0">
                  <thead>
                    <tr>
                      <th width="125px"> Frame</th>
                      <th width="100px"> Latitude</th>
                      <th width="100px"> Longitude</th>
                      <th width="215px"> Data da Deteção</th>
                      <th width="125px"> Percentagem da Deteção</th>
                      <th width="100px"> FPS </th>
                    </tr>
                  </thead>
                </table>
              </div>
            </div>
          </div>
        </div>
    `;
  

  for (const result of detections){
    const contentType = 'image/jpg';
    const blob = b64toBlob(result.frame, contentType);
    const blobUrl = URL.createObjectURL(blob);

    txtResultados += `
            
    <div class="container-fluid">
      <div class="card">
        <div class="card-body">
          <div class="table-responsive">
            <table class="table table-bordered" cellspacing="0">
              <tbody>
                <tr>
                  <td width="100px"><img style="display:block;" width="100px" height="70px" src="${blobUrl}"></td>    
                  <td width="100px"> ${result.latitude} </td>
                  <td width="100px"> ${result.longitude} </td>
                  <td width="215px"> ${result.dataDaDetecao} </td>
                  <td width="125px"> ${result.percentagemDaDetecao} </td>
                  <td width="100px"> ${result.fps} </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
          `;
  }
 
  resultados.innerHTML = txtResultados2;
  resultados.innerHTML += txtResultados;
  
})();
 

//-----------------------------------------
function hide(){
  document.getElementById('carouselExampleIndicators').style.display = 'none';
}

//-------------------------------------------------
//var video = document.querySelector("#videoElement");

/*function videoStream(){
if (navigator.mediaDevices.getUserMedia) {
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(function (stream) {
      video.srcObject = stream;
    })
    .catch(function (err0r) {
      console.log("Alguma coisa correu mal!");
    });
}

}
/*--------------------------------------------
function stop(e) {
  var stream = video.srcObject;
  var tracks = stream.getTracks();

  for (var i = 0; i < tracks.length; i++) {
    var track = tracks[i];
    track.stop();
  }

  video.srcObject = null;
}*/