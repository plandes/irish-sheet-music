# Latex document creation make file
# Created: 06/07/2012

# paths
TARG_DIR=	$(abspath target)
DERIVED_DIR=	derived
MKTUNETEX=	src/python/mktunetex.py
DATA_DIR=	data
TUNE_SPREAD=	$(abspath $(DATA_DIR)/tune-list.numbers)
ABC_SRC_DIR=	$(abspath $(DATA_DIR)/abc)
ABC_SRC=	$(notdir $(wildcard $(ABC_SRC_DIR)/*))
ABC_EPS=	$(patsubst %.abc,%.eps,$(addprefix $(TARG_DIR)/,$(ABC_SRC)))
TEX_SRC=	src/tex/$(TEX).tex
TEX_TARG=	$(TARG_DIR)/$(TEX).tex
TEX_DVI=	$(TARG_DIR)/$(TEX).dvi
TEX_PS=		$(TARG_DIR)/$(TEX).ps
TEX_PDF=	$(TARG_DIR)/$(TEX).pdf

# vars
TEX=		Tunes
LAT=		$(TPATH) latex

all:		derived

.PHONY:		info
info:
		@echo "eps: $(ABC_EPS)"

.PHONY:	derived
derived:	$(TEX_PDF)
		mkdir -p $(DERIVED_DIR)
		cp $(TEX_PDF) $(DERIVED_DIR)

$(TARG_DIR):
		mkdir -p $(TARG_DIR)

$(TARG_DIR)/%.abc:	$(ABC_SRC_DIR)/%.abc $(TARG_DIR)
		cat $< | grep -v -E '^[TO]:' > $@

$(TARG_DIR)/%.eps:	$(TARG_DIR)/%.abc
		abcm2ps -E -O $@ $<
		mv `echo $@ | sed 's/\(.*\)\.eps$$/\1001.eps/'` $@

$(TEX_TARG):	$(TARG_DIR) $(TEX_ORG)
		$(MKTUNETEX) $(TEX_SRC) $(ABC_SRC_DIR) $(TUNE_SPREAD) $(TEX_TARG) $(TARG_DIR)

$(TEX_DVI):	$(TARG_DIR) $(ABC_EPS) $(TEX_TARG)
		( cd $(TARG_DIR) ; $(LAT) $(TEX).tex )
		( cd $(TARG_DIR) ; $(LAT) $(TEX).tex )

$(TEX_PS):	$(TEX_DVI)
		( cd $(TARG_DIR) ; $(TPATH) dvips -o $(TEX).ps $(TEX).dvi )

$(TEX_PDF):	$(TEX_DVI)
		( cd $(TARG_DIR) ; $(TPATH) dvipdfm -p letter $(TEX).dvi )

.PHONY:
showpdf:	$(TEX_PDF)
		open $(TEX_PDF)
		osascript -e 'tell application "Emacs" to activate'

.PHONY:
clean:
		rm -fr $(TARG_DIR)
