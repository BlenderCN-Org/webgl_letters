CanonicalFont = function(letters) {
    var flatten = function(arrays) {
        return [].concat.apply([], arrays)
    }

    var get_normal = function(triangle) {
        return vectorProduct(
                vectorPoints(triangle[1], triangle[0]),
                vectorPoints(triangle[2], triangle[0])
        )
    }

    this.letters = {};
    
    var data = [];
    var data_index = 0;

    for (var symbol in letters) {
        this.letters[symbol] = {
            "kerning_width": letters[symbol].kerning_width,
            "start": data_index * 3,
            "vertex_count": letters[symbol].mesh.length * 3
        }
        var triangles = letters[symbol].mesh;
        for (var i = 0; i < triangles.length; i++) {
            normal = get_normal(triangles[i]);
            data.push(
                triangles[i][0][0], triangles[i][0][1], triangles[i][0][2],
                normal[0]     , normal[1]     , normal[2],

                triangles[i][1][0], triangles[i][1][1], triangles[i][1][2],
                normal[0]     , normal[1]     , normal[2],

                triangles[i][2][0], triangles[i][2][1], triangles[i][2][2],
                normal[0]     , normal[1]     , normal[2]
            );
            data_index++;
        }
    }

    var buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.STATIC_DRAW);
    this.buf = buf;
}

CanonicalFont.prototype.drawLetter = function(symbol) {
    gl.bindBuffer(gl.ARRAY_BUFFER, this.buf);

    gl.enableVertexAttribArray(aXYZ);
    gl.vertexAttribPointer(aXYZ, 3, gl.FLOAT, false, 6*FLOATS, 0*FLOATS);

    gl.enableVertexAttribArray(aNormal);
    gl.vertexAttribPointer(aNormal, 3, gl.FLOAT, false, 6*FLOATS, 3*FLOATS);

    var letter = this.letters[symbol];
    gl.drawArrays(gl.TRIANGLES, letter.start, letter.vertex_count);
}

CanonicalFont.prototype.isWhitespace = function(symbol) {
    return (this.letters[symbol].vertex_count == 0);
}

CanonicalFont.prototype.letterKerning = function(symbol) {
    return this.letters[symbol].kerning_width;
}

var fonts = {}
var font_data = {}

registerFont = function(name, data) {
    font_data[name] = data;
}

getFont = function(name) {
    font = fonts[name];
    if (!font) {
        font = new CanonicalFont(font_data[name]);
        delete font_data[name];
        fonts[name] = font;
    }
    return font;
}

Text = function(font_name, body, center, size) {
    this.font = getFont(font_name);

    this.center = center || [0, 0, 0];
    this.size = size || 1;
    this.color = [1,0.75,0];
    this.offset = undefined;
    this.rot = undefined;

    this.lineSpacing = 0.8;
    this.letterSpacing = 0;
    this.kerning = 1;
    this.centered = false;
    this.justified = false;

    this.condensation = 1;

    this.centerToOrigin = false;

    this.depth = 1;

    this.set(body)
}

Text.prototype.set = function(body) {
    this.lines = body.split('\n');
    this.lineWidths = [];
    this.lineWhitespaceCounts = [];
    this.width = 0;
    this.height = 0;

    var line_width = 0;
    var whitespace_count = 0;
    var letter_width = 0;
    for (var i = 0; i < this.lines.length; i++) {
        line_width = 0;
        whitespace_count = 0;
        for (var j = 0; j < this.lines[i].length; j++) {
            letter = this.lines[i][j];
            letter_width = this.font.letterKerning(letter) * this.kerning +
                           this.letterSpacing;
            line_width += letter_width;
            if (this.font.isWhitespace(letter)) {
                whitespace_count++;
            }

        }
        if (this.width < line_width) {
            this.width = line_width;
        }
        this.lineWidths.push(line_width);
        this.lineWhitespaceCounts.push(whitespace_count);
        this.height += this.lineSpacing;
    }
}

Text.prototype.draw = function() {
    pushMatrix();
    gl.vertexAttrib3fv(aColor, this.color); // подаваме цвета
    translate(this.center);
    if (this.rot)
    {
        if (this.rot[0]) zRotate(this.rot[0]);
        if (this.rot[1]) xRotate(this.rot[1]);
        if (this.rot[2]) zRotate(this.rot[2]);
    }
    scale([this.size * this.condensation, this.size, this.size * this.depth]);
    if (this.offset) translate(this.offset);

    if (this.centerToOrigin) {
        translate([-this.width/2, 0, 0]);
    }

    for (var i = 0; i < this.lines.length; i++) {
        pushMatrix();
        if (this.centered) {
            translate([(this.width - this.lineWidths[i]) / 2, 0, 0]);
        }
        for (var j = 0; j < this.lines[i].length; j++) {
            letter = this.lines[i][j];
            useMatrix();
            this.font.drawLetter(letter);
            if (this.justified && this.font.isWhitespace(letter)) {
                translate([
                    (this.width - this.lineWidths[i]) / this.lineWhitespaceCounts[i],
                    0, 0
                ]);
            }
            translate([this.font.letterKerning(letter) * this.kerning
                     + this.letterSpacing, 0, 0]);
        }
        popMatrix();
        translate([0, - this.lineSpacing, 0]);
    }

    popMatrix();
}
