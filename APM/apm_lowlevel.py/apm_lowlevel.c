/****************************************************************************

 $Id: apm_lowlevel.c,v 1.2 2003/04/30 20:31:30 riemer Exp $

 Copyright (C) 2002-2003 Tilo Riemer <riemer@lincvs.org>
 All rights reserved. 

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:

 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. The name of the author may not be used to endorse or promote products
    derived from this software without specific prior written permission. 

 THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
 IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
 INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
 NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
 THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

****************************************************************************/


#include <Python.h>

//we don't need it for Linux but for *BSD at the moment
//interface unstable!!!

extern int apm_state(int* p, int* t, int* ac);


/* wrapper function for apm_state() */
static PyObject* wrap_apm_state(PyObject* self, PyObject* args)
{
  int res, p, t, ac;

  res = apm_state(&p, &t, &ac);
  /* if (res == error) throw exception? 
     At the moment we passes the return value of apm_state to the return values
     of this wrapper...
   */
  
  return Py_BuildValue("iiii", res, p, t, ac);
}


/* get version of this module */
static PyObject* wrap_version(PyObject* self, PyObject* args)
{
  char version[] = "0.3";
  return Py_BuildValue("s", version);
}


/* array of functions */
static PyMethodDef apmMethods[] = {
  {"state", wrap_apm_state, METH_VARARGS},
  {"version", wrap_version, METH_VARARGS},
  {0}
};


/* init function (called at import apm_lowlevel) */
void initapm_lowlevel(void)
{
  Py_InitModule("apm_lowlevel", apmMethods);
}
