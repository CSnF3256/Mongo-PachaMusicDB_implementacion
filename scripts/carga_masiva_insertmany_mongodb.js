// Ejecutar en MongoDB Playground o mongosh.
// Carga inicial para tomar capturas si la base local todavía no tiene datos.
use('PachaMusicDB');

db.usuarios.drop();
db.artistas.drop();
db.albumes.drop();
db.canciones.drop();
db.playlists.drop();
db.ventas.drop();
db.pagos.drop();
db.reproducciones.drop();
db.interacciones.drop();

const usuario1 = ObjectId('65a100010000000000000001');
const usuario2 = ObjectId('65a100010000000000000002');
const artista1 = ObjectId('65a200010000000000000001');
const artista2 = ObjectId('65a200010000000000000002');
const album1 = ObjectId('65a300010000000000000001');
const album2 = ObjectId('65a300010000000000000002');
const cancion1 = ObjectId('65a400010000000000000001');
const cancion2 = ObjectId('65a400010000000000000002');
const cancion3 = ObjectId('65a400010000000000000003');

const usuariosJson = [
  {_id: usuario1, usuario_id_sql: 1, nombre_usuario: 'Camila Torres', email_usuario: 'camila.torres@email.com', pais_usuario: 'Ecuador', tipo_usuario: 'Premium', estado_usuario: 'Activo'},
  {_id: usuario2, usuario_id_sql: 2, nombre_usuario: 'Mateo Ruiz', email_usuario: 'mateo.ruiz@email.com', pais_usuario: 'Colombia', tipo_usuario: 'Free', estado_usuario: 'Activo'}
];

const artistasJson = [
  {_id: artista1, artista_id_sql: 1, nombre_artista: 'Killa Sound', pais_artista: 'Ecuador', estado: 'Activo', descripcion_artista: 'Proyecto musical andino contemporáneo.', discografica: {nombre_discografica: 'Pacha Records'}},
  {_id: artista2, artista_id_sql: 2, nombre_artista: 'Andes Beat', pais_artista: 'Perú', estado: 'Activo', descripcion_artista: 'Fusión electrónica latinoamericana.', discografica: {nombre_discografica: 'Digital Andes'}}
];

const albumesJson = [
  {_id: album1, album_id_sql: 1, nombre_album: 'Raíces Digitales', fecha_lanzamiento: '2026-01-15', estado_album: 'Publicado', artista: {artista_id: artista1, nombre_artista: 'Killa Sound'}},
  {_id: album2, album_id_sql: 2, nombre_album: 'Nodos del Sol', fecha_lanzamiento: '2026-03-10', estado_album: 'Publicado', artista: {artista_id: artista2, nombre_artista: 'Andes Beat'}}
];

const cancionesJson = [
  {_id: cancion1, cancion_id_sql: 1, titulo_cancion: 'Luz de Páramo', duracion_segundos: 214, estado_cancion: 'Activa', reproducciones_totales: 15320, likes_totales: 890, generos: ['Andina','Pop'], album: {album_id: album1, nombre_album: 'Raíces Digitales'}, artista: {artista_id: artista1, nombre_artista: 'Killa Sound'}},
  {_id: cancion2, cancion_id_sql: 2, titulo_cancion: 'Circuito Ancestral', duracion_segundos: 198, estado_cancion: 'Activa', reproducciones_totales: 11200, likes_totales: 720, generos: ['Electrónica','Andina'], album: {album_id: album1, nombre_album: 'Raíces Digitales'}, artista: {artista_id: artista1, nombre_artista: 'Killa Sound'}},
  {_id: cancion3, cancion_id_sql: 3, titulo_cancion: 'Sol de Datos', duracion_segundos: 240, estado_cancion: 'Activa', reproducciones_totales: 8900, likes_totales: 540, generos: ['Pop','Fusión'], album: {album_id: album2, nombre_album: 'Nodos del Sol'}, artista: {artista_id: artista2, nombre_artista: 'Andes Beat'}}
];

const playlistsJson = [
  {_id: ObjectId('65a500010000000000000001'), playlist_id_sql: 1, nombre_playlist: 'Favoritas Andinas', tipo_playlist: 'Privada', estado: 'Activa', usuario: {usuario_id: usuario1, nombre_usuario: 'Camila Torres'}, canciones: [{cancion_id: cancion1, titulo_cancion: 'Luz de Páramo', nombre_artista: 'Killa Sound'}, {cancion_id: cancion2, titulo_cancion: 'Circuito Ancestral', nombre_artista: 'Killa Sound'}]}
];

const ventasJson = [
  {_id: ObjectId('65a600010000000000000001'), venta_id_sql: 1, usuario: {usuario_id: usuario1, nombre_usuario: 'Camila Torres'}, fecha_venta: new Date('2026-06-01'), total_venta: 9.99, estado_venta: 'Pagada', tipo_contenido: 'Suscripcion', detalles: [{concepto: 'Plan Premium mensual', precio: 9.99, cantidad: 1}]},
  {_id: ObjectId('65a600010000000000000002'), venta_id_sql: 2, usuario: {usuario_id: usuario2, nombre_usuario: 'Mateo Ruiz'}, fecha_venta: new Date('2026-06-05'), total_venta: 1.99, estado_venta: 'Pendiente', tipo_contenido: 'Cancion', detalles: [{cancion_id: cancion3, titulo_cancion: 'Sol de Datos', precio: 1.99, cantidad: 1}]}
];

const pagosJson = [
  {_id: ObjectId('65a700010000000000000001'), pago_id_sql: 1, usuario_id: usuario1, monto_pago: 9.99, metodo_pago: 'Tarjeta', estado_pago: 'aprobado', fecha_pago: new Date('2026-06-01')}
];

const reproduccionesJson = [
  {_id: ObjectId('65a800010000000000000001'), reproduccion_id_sql: 1, usuario_id: usuario1, cancion_id: cancion1, fecha_reproduccion: new Date('2026-06-10'), duracion_escuchada: 214, omitida: 'NO', dispositivo: 'Web'},
  {_id: ObjectId('65a800010000000000000002'), reproduccion_id_sql: 2, usuario_id: usuario2, cancion_id: cancion2, fecha_reproduccion: new Date('2026-06-11'), duracion_escuchada: 120, omitida: 'SI', dispositivo: 'Móvil'}
];

const interaccionesJson = [
  {_id: ObjectId('65a900010000000000000001'), usuario_id: usuario1, cancion_id: cancion1, tipo_interaccion: 'like', fecha_interaccion: new Date('2026-06-10')}
];

db.usuarios.insertMany(usuariosJson);
db.artistas.insertMany(artistasJson);
db.albumes.insertMany(albumesJson);
db.canciones.insertMany(cancionesJson);
db.playlists.insertMany(playlistsJson);
db.ventas.insertMany(ventasJson);
db.pagos.insertMany(pagosJson);
db.reproducciones.insertMany(reproduccionesJson);
db.interacciones.insertMany(interaccionesJson);

db.usuarios.createIndex({email_usuario: 1}, {name: 'idx_usuarios_email'});
db.usuarios.createIndex({tipo_usuario: 1, pais_usuario: 1}, {name: 'idx_usuarios_tipo_pais'});
db.artistas.createIndex({nombre_artista: 1}, {name: 'idx_artistas_nombre'});
db.albumes.createIndex({'artista.artista_id': 1}, {name: 'idx_albumes_artista'});
db.canciones.createIndex({titulo_cancion: 1}, {name: 'idx_canciones_titulo'});
db.canciones.createIndex({generos: 1}, {name: 'idx_canciones_generos'});
db.canciones.createIndex({reproducciones_totales: -1}, {name: 'idx_canciones_reproducciones'});

print('Carga masiva completada con insertMany() en PachaMusicDB.');
