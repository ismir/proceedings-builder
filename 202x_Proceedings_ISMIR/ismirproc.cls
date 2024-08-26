%%
%% FILE: ismirproc.cls
%%
%% USAGE: \documentclass[<book-options>]{ismirproc}
%%
%% PURPOSE: LaTeX2e class file for the ISMIR proceedings
%%
%% Johan Pauwels (j.pauwels@qmul.ac.uk)
%%
%% \includepaper command adapted from confproc.cls
%%
%% This system is distributed in the hope that it will be useful,
%% but WITHOUT ANY WARRANTY; without even the implied warranty of
%% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
%%


\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{ismirproc}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{book}}
\ProcessOptions
\LoadClass[10pt, twoside, a4paper]{book}
\RequirePackage[T1]{fontenc}
\RequirePackage[utf8]{inputenc}
\RequirePackage{fancyhdr}
\RequirePackage[inner=2.2cm,outer=1.8cm,top=2.8cm,bottom=3.0cm]{geometry}
\RequirePackage{pdfpages}
\RequirePackage{authorindex}
\RequirePackage{url}
\RequirePackage{multicol}
\RequirePackage{setspace}
\RequirePackage{mathptmx}  % Use times font for text and math
\RequirePackage[scaled]{helvet}
\RequirePackage{verse}
\RequirePackage{emptypage}
\RequirePackage{tabularx}
\RequirePackage{booktabs}
\RequirePackage{titlesec}
\RequirePackage{hyperref}


\graphicspath{ {./logos/} }
% Custom environment to auto-indent long reviewers when split over two lines
\newenvironment{reviewers}
 {\setlength{\leftmargini}{0em}%
  \setlength{\vindent}{1em}%
  \begin{verse}}
 {\end{verse}}
% Custom colours for sponsor section
\definecolor{platinum}{gray}{0.82}
\definecolor{gold}{RGB}{191, 144, 0}
\definecolor{silver}{RGB}{183, 183, 183}
% Vertical centering of logos
\renewcommand\tabularxcolumn[1]{m{#1}}
% Use space between paragraphs instead of indentation
\setlength{\parskip}{\medskipamount}
\setlength{\parindent}{0pt}
% Colour links
\hypersetup{colorlinks=true, urlcolor=Blue, linkcolor=black}

\newcommand*{\speaker}[1]{\textsf{\Large #1}}

% Include fonts from embedded pdfs even if they already exist
% http://tex.stackexchange.com/q/162711/97428
\pdfinclusioncopyfonts 1
\pdfminorversion=7

%
% Header/footer layout
%
\pagestyle{fancy}
\setlength{\footskip}{50pt}
\lhead[\proctitle]{}
\rhead[]{\proctitle}
\lfoot{}
\cfoot{\thepage}

%
% Included article layout (twoside offset)
%
\includepdfset{offset=2mm 0}

\makeatletter
\def\addtoauthorindex#1{%
  \@for\@myauth:=#1\do{\aimention{\@myauth}}}
\makeatother
% New command to add pdf articles run like following:
% \includepaper[offset]{title}{comma_separated_authors}{pdffile}
\newsavebox\mybox
\newcommand{\includepaper}[4][0 -7mm]{%
  \refstepcounter{subsection}
  \phantomsection
  \addcontentsline{toc}{section}{#2\texorpdfstring{\\\textit{#3}}{}}%
  \addtoauthorindex{#3}
  % this is to get the number of pages in the pdf
  \savebox\mybox{\includegraphics{#4}}
  \ifthenelse{\pdflastximagepages>1}{% pdftex
    % include first page without headers
    \includepdf[scale=1.0,offset=#1, pages=1,pagecommand=\thispagestyle{plain}]{#4}%
    % include remaining pages with headers
    \includepdf[scale=1.0,offset=#1, pages=2-,pagecommand=\thispagestyle{fancy}]{#4}%
  }{%
    \includepdf[scale=1/0,offset=#1, pages=1,pagecommand=\thispagestyle{plain}]{#4}%
  }
}

\endinput
