// game.js — Phaser 3 compatible top-down demo (pre-3.50 support)

const config = {
  type: Phaser.AUTO,
  width: 960,
  height: 640,
  parent: 'game-container',
  physics: {
    default: 'arcade',
    arcade: { debug: false, gravity: { y: 0 } }
  },
  scene: { preload, create, update }
};

const TILE_SIZE = 32;
const MAP_W = 30;
const MAP_H = 20;

const ASSET_PATHS = {
  tileset: 'assets/tileset/1.1 Tiles/Tileset2.png',
  fields: 'assets/tileset/1 Tiles/FieldsTileset.png',
  house: 'assets/tileset/2 Objects/7 House/1.png',
  player_idle: 'assets/character/PNG/Sword/Without_shadow/Sword_Idle_without_shadow.png',
  player_walk: 'assets/character/PNG/Sword/Without_shadow/Sword_Walk_without_shadow.png',
  player_attack: 'assets/character/PNG/Sword/Without_shadow/Sword_attack_without_shadow.png'
};

let game = new Phaser.Game(config);

function preload() {
  // Load images & spritesheets
  this.load.image('tilesetImg', ASSET_PATHS.tileset);
  this.load.image('fieldsImg', ASSET_PATHS.fields);
  this.load.image('house', ASSET_PATHS.house);

  this.load.spritesheet('player_idle', ASSET_PATHS.player_idle, { frameWidth: 32, frameHeight: 32 });
  this.load.spritesheet('player_walk', ASSET_PATHS.player_walk, { frameWidth: 32, frameHeight: 32 });
  this.load.spritesheet('player_attack', ASSET_PATHS.player_attack, { frameWidth: 32, frameHeight: 32 });

  this.load.bitmapFont('arcade', 'https://labs.phaser.io/assets/fonts/bitmap/arcade.png', 'https://labs.phaser.io/assets/fonts/bitmap/arcade.xml');
}

function create() {
  const scene = this;

  console.log('Tileset loaded?', this.textures.exists('tilesetImg'));

  // === TILEMAP CREATION (Older Phaser compatible) ===
  // 1. Create a 2D array for map data
  const mapData = [];
  for (let y = 0; y < MAP_H; y++) {
    const row = [];
    for (let x = 0; x < MAP_W; x++) {
      row.push(0); // initial tile index
    }
    mapData.push(row);
  }

  // 2. Create the tilemap from the 2D array
  const map = this.make.tilemap({ data: mapData, tileWidth: TILE_SIZE, tileHeight: TILE_SIZE });

  // 3. Add tileset
  const tileset = map.addTilesetImage('tilesetImg', 'tilesetImg', TILE_SIZE, TILE_SIZE, 0, 0);

  // 4. Create layer
  const layer = map.createLayer(0, tileset, 0, 0);

  // 5. Fill tiles randomly
  for (let y = 0; y < MAP_H; y++) {
    for (let x = 0; x < MAP_W; x++) {
      const index = Phaser.Math.Between(0, 8);
      layer.putTileAt(index, x, y);
    }
  }

  // === OBSTACLES ===
  const obstacles = scene.physics.add.staticGroup();
  const housePositions = [
    { x: 6 * TILE_SIZE + TILE_SIZE/2, y: 4 * TILE_SIZE + TILE_SIZE/2 },
    { x: 22 * TILE_SIZE + TILE_SIZE/2, y: 7 * TILE_SIZE + TILE_SIZE/2 },
    { x: 12 * TILE_SIZE + TILE_SIZE/2, y: 14 * TILE_SIZE + TILE_SIZE/2 }
  ];

  housePositions.forEach(pos => {
    try {
      const house = scene.add.image(pos.x, pos.y, 'house').setOrigin(0.5);
      obstacles.add(house);
      scene.physics.world.enable(house, Phaser.Physics.Arcade.STATIC_BODY);
      house.body.setSize(house.width * 0.9, house.height * 0.9);
    } catch (e) {
      console.warn('House image failed to load:', e);
    }
  });

  // === PLAYER ===
  this.player = this.physics.add.sprite(3 * TILE_SIZE, 10 * TILE_SIZE, 'player_idle', 0);
  this.player.setCollideWorldBounds(true);
  this.player.speed = 120;
  this.player.hp = 8;
  this.player.setDepth(10);
  this.physics.add.collider(this.player, obstacles);

  // === ENEMY ===
  this.enemy = this.physics.add.sprite(18 * TILE_SIZE, 10 * TILE_SIZE, 'player_idle', 0);
  this.enemy.setCollideWorldBounds(true);
  this.enemy.tint = 0xff8888;
  this.enemy.health = 4;
  this.physics.add.collider(this.enemy, obstacles, (en) => {
    en.body.velocity.x *= -1;
    en.body.velocity.y *= -1;
  });

  // === ANIMATIONS ===
  this.anims.create({ key: 'idle', frames: this.anims.generateFrameNumbers('player_idle', { start: 0, end: 3 }), frameRate: 6, repeat: -1 });
  this.anims.create({ key: 'walk', frames: this.anims.generateFrameNumbers('player_walk', { start: 0, end: 7 }), frameRate: 10, repeat: -1 });
  this.anims.create({ key: 'attack', frames: this.anims.generateFrameNumbers('player_attack', { start: 0, end: 5 }), frameRate: 16, repeat: 0 });

  // === CAMERA ===
  this.cameras.main.setBounds(0, 0, MAP_W * TILE_SIZE, MAP_H * TILE_SIZE);
  this.cameras.main.startFollow(this.player, true, 0.08, 0.08);

  // === INPUT ===
  this.cursors = this.input.keyboard.createCursorKeys();
  this.keys = this.input.keyboard.addKeys({
    W: Phaser.Input.Keyboard.KeyCodes.W,
    A: Phaser.Input.Keyboard.KeyCodes.A,
    S: Phaser.Input.Keyboard.KeyCodes.S,
    D: Phaser.Input.Keyboard.KeyCodes.D,
    SPACE: Phaser.Input.Keyboard.KeyCodes.SPACE
  });

  // === HUD ===
  this.hpText = this.add.bitmapText(12, 10, 'arcade', 'HP: ' + this.player.hp, 16).setScrollFactor(0);

  // === COLLISIONS & ATTACKS ===
  this.lastPlayerHit = 0;
  this.physics.add.overlap(this.player, this.enemy, (p, e) => {
    const now = Date.now();
    if (now - this.lastPlayerHit < 800) return;
    this.lastPlayerHit = now;
    p.hp = Math.max(0, p.hp - 1);
    p.setTint(0xffaaaa);
    scene.time.delayedCall(250, () => p.clearTint());
    if (p.hp <= 0) {
      p.setTint(0x000000);
      p.setVelocity(0, 0);
      p.anims.stop();
    }
  });

  this.lastAttack = 0;
  this.keys.SPACE.on('down', () => {
    const now = Date.now();
    if (now - this.lastAttack < 600) return;
    this.lastAttack = now;
    this.player.play('attack', true);
    const dist = Phaser.Math.Distance.Between(this.player.x, this.player.y, this.enemy.x, this.enemy.y);
    if (dist < 48 && this.enemy.active) {
      this.enemy.health -= 1;
      this.enemy.setTint(0xffcccc);
      scene.time.delayedCall(120, () => this.enemy.clearTint());
      if (this.enemy.health <= 0) this.enemy.disableBody(true, true);
    }
  });
}

function update(time) {
  if (!this.player.active) return;

  // Movement
  const speed = this.player.speed;
  let vx = 0, vy = 0;
  if (this.cursors.left.isDown || this.keys.A.isDown) vx = -speed;
  else if (this.cursors.right.isDown || this.keys.D.isDown) vx = speed;
  if (this.cursors.up.isDown || this.keys.W.isDown) vy = -speed;
  else if (this.cursors.down.isDown || this.keys.S.isDown) vy = speed;
  this.player.setVelocity(vx, vy);

  // Animations
  if (vx !== 0 || vy !== 0) this.player.play('walk', true);
  else this.player.play('idle', true);

  // HUD
  this.hpText.setText('HP: ' + this.player.hp);

  // Enemy wandering
  if (this.enemy.active) {
    if (!this.enemy._nextChange) this.enemy._nextChange = 0;
    if (time > this.enemy._nextChange) {
      this.enemy._nextChange = time + Phaser.Math.Between(500, 1500);
      const angle = Phaser.Math.FloatBetween(0, Math.PI * 2);
      const sp = Phaser.Math.Between(20, 60);
      this.enemy.body.setVelocity(Math.cos(angle) * sp, Math.sin(angle) * sp);
    }
  }
}
