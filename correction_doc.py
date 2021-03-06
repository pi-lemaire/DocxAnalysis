# coding: utf-8
from docx import Document
from lxml import etree
import sys
import glob, os
import io
from path import Path

def introspection(variable):
  L = dir(variable)
  for v in L:
      if (str(v).startswith("_")):
           continue
      if (v == "part"):
          continue
      print(v + "= " + str(getattr(variable, v)))

def isBold(style):
  print("Gras: " +  ("Non", "Oui") [bool(style.font.bold) == True])

def isItalic(style):
  print("Italique: " + ("Non", "Oui") [bool(style.font.italic) == True])

def alignment(style):
    if (not style.paragraph_format):
        return

    print("Alignement: " + str(style.paragraph_format.alignment))
    if (style.paragraph_format.space_before and style.paragraph_format.space_after):
      print("Espace avant: " + str(style.paragraph_format.space_before.pt))
      print("Espace apres: " + str(style.paragraph_format.space_after.pt))
      print("Saut de page avant: " + str(style.paragraph_format.page_break_before))

def fontSize(style):
    if (not style.font.size):
        return
    print("Taille police: " + str(style.font.size.pt))

def fontColor(style):
    if (not style.font.color):
        return
    print("Couleur police: " + str(style.font.color.rgb))

def border(style):
  xml_str = style.element.xml
  root = etree.fromstring(xml_str)
  ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
  ns_pfx = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
  pgSz_el = root.find('.//w:pBdr', ns)
  top = root.find('.//w:top', ns)
  bottom = root.find('.//w:bottom', ns)
  left = root.find('.//w:left', ns)
  right = root.find('.//w:right', ns)

  pgMar_el = root.find('.//w:shd', ns)
  border = ''
  if (top is not None):
    border += "t"
  if (bottom is not None):
    border += "b"
  if (right is not None):
    border += "r"
  if (left is not None):
    border += "l"
  if (pgSz_el is not None):
    print("Bordure: " + border)
  if (pgMar_el is not None):
    print("Bordure couleur: " + str(pgMar_el.get(ns_pfx + 'fill')))


def checkStyles(styles, styleNames):
    for s in styles:
      if (s.name.lower() in (name.lower() for name in styleNames)):
        print("---")
        print(s.name)
        isBold(s)
        isItalic(s)
        alignment(s)
        fontSize(s)
        fontColor(s)
        border(s)

def isempty(par):
  p = par._p
  runs = p.xpath('./w:r[./*[not(self::w:rPr)]]')
  others = p.xpath('./*[not(self::w:pPr) and not(self::w:r)] and '
                   'not(contains(local-name(), "bookmark"))')
  return len(runs) == 0


def checkEmptyParagraphs(paragraphs):
  count = 0
  for p in paragraphs:
    if (isempty(p)):
      count += 1
  print("Nombre de paragraphes vides = " + str(count) + "/103 au depart")

def textToStyle(paragraphs, styleName, text):
  countStyle = 0.0
  countTotal = 0.0
  for paragraph in paragraphs:
    for run in paragraph.runs:
      for t in text:
        if t in run.text:
          countTotal+=1
          if paragraph.style.name.lower() == styleName.lower():
            countStyle+=1
  if (countTotal == 0):
    return 0,0.1
  return countStyle,countTotal


def checkStylesApplied(paragraphs):
  nTitle = textToStyle(paragraphs, "Title", ["Livre de recettes"])
  nType = textToStyle(paragraphs, "Heading 1", [u"Entrées", "Plats", "Desserts"])
  nHeading3 = textToStyle(paragraphs, "Heading 3", [u"Ingrédients", u"Réalisation"])
  nRecap = textToStyle(paragraphs, "Description", [u"Préparation\u00A0:"])
  print("Style Titre=" + str(nTitle*100) +"%")
  print("Style Titre1=" + str(nType*100) + "%")
  print("Style Titre3=" + str(nHeading3*100) + "%")
  print("Style Description=" + str(nRecap*100) + "%")

def checkAltText(images):
  for im in images:
    print (im._inline.docPr.get("descr"))





styleNames = ["Heading 1", "Description", "Title", "Heading 2", "Heading 3"]

analyzeDir = sys.argv[1]

for f in Path(analyzeDir).walkfiles():
    if not (f.ext==".docx" or f.ext==".DOCX"):
        continue
    
    
    print("===================")
    
    #currStudentName=os.path.basename(os.path.normpath(f.dirname()))
    #currStudentName = currStudentName[0:currStudentName.find('_')]
    foldersPath = os.path.normpath(f.dirname())
    lastSlash = foldersPath.rfind("/")
    prevSlash = foldersPath[0:lastSlash-1].rfind("/")
    studentFolder = foldersPath[prevSlash+1:lastSlash-1]
    print(studentFolder[0:studentFolder.find('_')])
    
    print("----")
    
    #continue
    
    filename = f.abspath()
    
        
    print(filename)
    
    print("-----")

    #filename = sys.argv[1]
    f = open(filename, 'rb')
    
    
    try:
        document = Document(f)
    except:
        print("######## ERREUR : ouverture document impossible")
        continue
    

    

    styles = document.styles
    paragraphs = document.paragraphs
    images = document.inline_shapes

    # print("---")
    # checkStyles(styles, styleNames)
    # print("---")
    # checkEmptyParagraphs(paragraphs)
    # print("---")
    # print("Taux d'application des styles:")
    # checkStylesApplied(paragraphs)
    # print("---")
    # print("Numéros de pages + table des matieres : à vérifier dans le docx")
    # print("---")
    # print("Texte remplacement premiere photo=" + str(images[0]._inline.docPr.get("descr")))
    # print("Texte remplacement toutes photos")
    # checkAltText(images)


    try:
        cTitle,cTitleTotal = textToStyle(paragraphs, "Title", ["Livre de recettes"])
        cHeading3, cHeading3Total = textToStyle(paragraphs, "Heading 3", [u"Ingrédients", u"Réalisation"])
        cRecap, cRecapTotal = textToStyle(paragraphs, "Description", [u"Préparation\u00A0:"])
        alt = images[0]._inline.docPr.get("descr")

        if (int(cTitleTotal) ==0):
          print("W1. Probleme detecte, verifier le docx")
        else:
          print("W1 Appl Titre. " + str(cTitle/cTitleTotal*100) +"% (" + str(int(cTitleTotal)) + "/" + str(int(cTitle)) + ")")
        print("W2 nom prenom. : verif docx")
        print("W3. ")
        checkEmptyParagraphs(paragraphs)
        print("W4 saut 1ere page. verif docx")
        if (int(cHeading3Total) ==0):
          print("W5. Probleme detecte, verifier le docx")
        else:
          print("W5 Appl Titre 3. " + str(cHeading3/cHeading3Total*100) +"% (" + str(int(cHeading3)) + "/" + str(int(cHeading3Total)) + ")")
        print("W6 7 8 10. " + str(checkStyles(styles, styleNames)))
        if (int(cRecapTotal) ==0):
          print("W9. Probleme detecte, verifier le docx")
        else:
          print("W9 Appl Descr. " + str(cRecap/cRecapTotal*100) +"% (" + str(int(cRecap)) + "/" + str(int(cRecapTotal)) + ")")
        print("W10. Saut de page recette/type plat : voir recap styles plus haut")
        print("W11 numero page. : verif docx")
        print("W12 tdm. verif docx ")
        print("W13 alt." + ("None",alt)[alt != None])
    except:
        print("######## ERREUR : le script n'a pas pu tourner normalement sur ce document")
        continue
    
    f.close()
    

