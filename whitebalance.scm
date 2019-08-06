; ### START COPIED SCRIPT ###

; Whitebalance is a script for The GIMP
; Adapted slightly to work with GIMP 2.10
;
; Description: converts the color temperature of an image 
;
; Last changed: August 5, 2019
;
; Copyright (C) 2006-2009 Luca de Alfaro <lda@dealfaro.org>
; Copyright (C) 2019 Jack Duvall <theduvallj@gmail.com>
;
; With many thanks to Martin Rogge <marogge@onlinehome.de>, 
; from whose grey-point script this is inspired. 
;
; --------------------------------------------------------------------
; 
; This program is free software; you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation; either version 2 of the License, or
; (at your option) any later version.  
; 
; This program is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
; 
; You should have received a copy of the GNU General Public License
; along with this program; if not, write to the Free Software
; Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
;

(define (script-fu-whitebalance image drawable mode amount intensmult satura)

  (define (floor x) (- x (fmod x 1)))

; Converts from linear to gamma-corrected sRGB [0,1]
  (define (togamma x)
    (if (<= x 0.00304)
	(* x 12.92)
	(let* ((exponent (/ 1 2.4)))
	  (- (* 1.055 (pow x exponent)) 0.055))))
	       
; Converts from linear to gamma-corrected sRGB [0,255]
  (define (togamma255 x)
    (max (min (floor (* 256 (togamma x))) 255) 0))

; Converts from gamma-corrected sRGB [0,1] to linear
  (define (tolinear y)
    (if (<= y 0.0392768)
	(/ y 12.92)
	(let* ((ratio (/ (+ y 0.055) 1.055)))
	  (pow ratio 2.4))))

; Converts from gamma-corrected sRGB [0,255] to linear
  (define (to255linear y)
    (tolinear (/ y 255)))

; Applies a ratio (in linear space) to sRGB values, where the sRGB
; values are scaled 0..255. 
  (define (lin-mult-in-gamma-space y255 r)
    (togamma255 (* r (to255linear y255))))

; Multiplication in the gamma space
  (define (linemult y r)
    (max (min (floor (* y r)) 255) 0))

; Makes the target be the average of the foreground, for gamma-colors
  (define (makegreyg r g b)
    (let* ((avg (/ (+ r (+ g b)) 3)))
      (list avg avg avg)))

; Makes the target be the average of the foreground, for linear colors
; Goal: keep the intensity constant 
  (define (makegrey r g b)
    (let* ((avg (+ (+ (* 0.2125 r) (* 0.7154 g)) (* 0.0721 b))))
      (list avg avg avg)))

; Makes the target be the linear colors of the background
  (define (linearcols l)
    (let* ((r (to255linear (car   l)))
	   (g (to255linear (cadr  l)))
	   (b (to255linear (caddr l))))
      (list r g b)))

; This is the color table, taken from
; http://www.vendian.org/mncharity/dir3/blackbody/UnstableURLs/bbr_color.html 
	(let* (
	 ; Foreground and background
         (fg (car (gimp-context-get-foreground)))
         (bg (car (gimp-context-get-background)))
	 ; Conversion amount
	 (a (/ amount 100))

	 ; LINEAR PORTION

	 ; Source colors, 0..255
	 (sbr (car   fg))
	 (sbg (cadr  fg))
	 (sbb (caddr fg))
	 ; Source colors, linear
	 (sr (to255linear sbr))
	 (sg (to255linear sbg))
	 (sb (to255linear sbb))
	 ; Finds the target colors, linear 
	            ; average of fg colors 
	 (tcs (cond ((= mode 0) (makegrey sr sg sb))
		    ; taken from background
		    ((= mode 1) (linearcols bg))))
	 ; Extracts the target colors
	 (tr (car   tcs))
	 (tg (cadr  tcs))
	 (tb (caddr tcs))
	 ; computes the ratios.  If the source is 0, no conversion happens.
	 (rra (if (= sbr 0) 1 (/ tr sr)))
	 (rga (if (= sbg 0) 1 (/ tg sg)))
	 (rba (if (= sbb 0) 1 (/ tb sb)))
	 ; Takes into account the conversion amount. 
	 (rr  (+ 1 (* a (- rra 1))))
	 (rg  (+ 1 (* a (- rga 1))))
	 (rb  (+ 1 (* a (- rba 1))))
	 ; Multiplies them by the intensity modification 
	 (m (/ intensmult 100))
	 ; And these are the real ratios, linear 
	 (rratio (* rr m))
	 (gratio (* rg m))
	 (bratio (* rb m))

         (i 0)
         (num_bytes 256)
         (red-curve   (cons-array num_bytes 'byte))
         (green-curve (cons-array num_bytes 'byte))
         (blue-curve  (cons-array num_bytes 'byte)))

    (gimp-image-undo-group-start image)

    (while (< i num_bytes)
	   (aset red-curve   i (lin-mult-in-gamma-space i rratio))
	   (aset green-curve i (lin-mult-in-gamma-space i gratio))
	   (aset blue-curve  i (lin-mult-in-gamma-space i bratio))
	   (set! i (+ i 1)))

    (gimp-curves-explicit drawable HISTOGRAM-RED   num_bytes red-curve  )
    (gimp-curves-explicit drawable HISTOGRAM-GREEN num_bytes green-curve)
    (gimp-curves-explicit drawable HISTOGRAM-BLUE  num_bytes blue-curve )

    (gimp-hue-saturation drawable 0 0.0 0.0 satura)

    (gimp-image-undo-group-end image)
    (gimp-displays-flush)
))

(script-fu-register
  "script-fu-whitebalance"
  "White balance"
  "White Balance 2.1\n\nFor help, go to http://luca.dealfaro.org/Whitebalance"
  "Luca de Alfaro <lda@dealfaro.org>"
  "Luca de Alfaro"
  "2006-2008"
  "RGB*"
  SF-IMAGE    "Image"         0
  SF-DRAWABLE "Drawable"      0
  SF-OPTION      "Mode" '("Make foreground gray" "Convert foreground to background")
  SF-ADJUSTMENT "Conversion amount (%)" '(100 0 100 1 10 0 0)
  SF-ADJUSTMENT "New intensity (%)" '(100 0 200 1 10 0 0)
  SF-ADJUSTMENT "Saturation change (%)" '(0 -100 100 1 10 0 0)
)
(script-fu-menu-register "script-fu-whitebalance" "<Image>/Filters/Colors")

; ### END COPIED SCRIPT ###

(define (script-fu-whiten-image 
    inImage 
    inDrawable 
  )
  (let* (
      (card-color (car (gimp-image-pick-color inImage inDrawable 5 5 TRUE TRUE 5)))
      (prev-fg (car (gimp-context-get-foreground)))
      (prev-bg (car (gimp-context-get-background)))
    )
    (let* (
        (r (car card-color))
        (g (cadr card-color))
        (b (caddr card-color))
      )
      (gimp-context-set-foreground (list r g b))
      
    )
    (gimp-context-set-background '(255 255 255))
    
    (script-fu-whitebalance inImage inDrawable 1 100 130 0)
    
    (gimp-image-undo-group-start image)
    (gimp-drawable-brightness-contrast inDrawable (/ -20 127) (/ 20 127))
    (gimp-image-undo-group-end image)
    
    (gimp-context-set-foreground prev-fg)
    (gimp-context-set-background prev-bg)
    (gimp-displays-flush)
  )
)

(define (script-fu-whiten-file filename)
  (let* (
      (image (car (gimp-file-load RUN-NOINTERACTIVE filename filename)))
      (drawable (car (gimp-image-get-active-layer image)))
    )
    (script-fu-whiten-image image drawable)
    (gimp-file-save RUN-NOINTERACTIVE image drawable filename filename)
    (gimp-image-delete image)
  )
)

(define (script-fu-whiten-multiple-files pattern)
  (let* (
      (filelist (cadr (file-glob pattern 1)))
    )
    (while (not (null? filelist))
      (let* (
          (filename (car filelist))
        )
        (script-fu-whiten-file filename)
      )
      (set! filelist (cdr filelist))
    )
  )
)

(script-fu-register
	"script-fu-whiten-image"							; func name
	"Correct 1KBWC Image"									      ; menu label
	"Corrects a photographed image of a 1KBWC card by\
	  adjusting color temperature and contrast"	; description
	"Jack Duvall"											          ; author
	"copyright 2019, Jack Duvall"							  ; copyright notice
	"August 5, 2019"										        ; date created
	"RGB*"													              ; type of image it works on
	SF-IMAGE		"Image"		0
	SF-DRAWABLE 	"Layer"		0
)
(script-fu-menu-register "script-fu-whiten-image" "<Image>/Filters/Colors")